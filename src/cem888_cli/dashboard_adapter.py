#!/usr/bin/env python3
"""
CEM888 Dashboard Matrix Adapter
Connects the agent to the sovereign dashboard via Matrix protocol.

Usage:
    python3 dashboard_adapter.py --profile BetaBot

Reads CEM_API_TOKEN and Matrix credentials from profile config,
connects to the Matrix homeserver, and relays messages between
the dashboard chat room and the agent.
"""

import asyncio
import json
import os
import sys
import signal
import argparse
import time
from pathlib import Path

try:
    from matrix_client.client import MatrixClient
    from matrix_client.api import MatrixHttpApi
except ImportError:
    # Fallback: use raw HTTP + polling
    MatrixClient = None
    MatrixHttpApi = None

try:
    import aiohttp
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
    import aiohttp

HOMESERVER = "https://cem888.ai"
MATRIX_BASE = f"{HOMESERVER}/_matrix"
POLL_INTERVAL = 2  # seconds


def load_config(profile_name: str) -> dict:
    """Load agent config from profile directory."""
    cem_dir = Path(os.environ.get("HOME", os.path.expanduser("~"))) / ".cem888"
    profile_dir = cem_dir / "profiles" / profile_name
    env_file = profile_dir / ".env"

    token = None
    mx_token = None
    mx_user = None
    mx_room = None

    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("CEM_API_TOKEN="):
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("MATRIX_ACCESS_TOKEN="):
                mx_token = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("MATRIX_USER_ID="):
                mx_user = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("MATRIX_ROOM_ID="):
                mx_room = line.split("=", 1)[1].strip().strip('"').strip("'")

    # If Matrix creds aren't in .env, try to re-register via ONBOARD
    if not mx_token and token:
        print(f"[*] Matrix credentials not found — re-onboarding {profile_name}...")
        mx_creds = onboard_matrix(profile_name, token)
        if mx_creds:
            mx_token = mx_creds.get("access_token", "")
            mx_user = mx_creds.get("user_id", "")
            mx_room = mx_creds.get("room_id", "")
            # Save to .env
            if env_file.exists():
                lines = env_file.read_text().splitlines()
                new_lines = []
                for line in lines:
                    if not line.startswith(("MATRIX_ACCESS_TOKEN=", "MATRIX_USER_ID=", "MATRIX_ROOM_ID=")):
                        new_lines.append(line)
                new_lines.append(f"MATRIX_ACCESS_TOKEN={mx_token}")
                new_lines.append(f"MATRIX_USER_ID={mx_user}")
                if mx_room:
                    new_lines.append(f"MATRIX_ROOM_ID={mx_room}")
                env_file.write_text("\n".join(new_lines) + "\n")

    return {
        "agent_name": profile_name,
        "token": token,
        "mx_token": mx_token,
        "mx_user": mx_user,
        "mx_room": mx_room,
        "profile_dir": str(profile_dir),
    }


def onboard_matrix(agent_name: str, cem_token: str) -> dict:
    """Re-register with ONBOARD to get Matrix credentials."""
    try:
        import urllib.request
        import urllib.error

        data = json.dumps({
            "agent_id": agent_name,
            "customer_id": f"reboard-{agent_name.lower()}",
            "name": agent_name,
            "email": "",
        }).encode()
        req = urllib.request.Request(
            "https://cem888.ai/api/create-token",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            mx = result.get("matrix", {})
            if mx:
                print(f"[+] Matrix onboarded: {mx.get('user_id')}")
            return mx
    except Exception as e:
        print(f"[!] ONBOARD failed: {e}")
        return {}


async def matrix_sync_loop(config: dict):
    """Poll Matrix for new messages and process them."""
    mx_token = config["mx_token"]
    mx_user = config["mx_user"]
    mx_room = config["mx_room"]
    agent_name = config["agent_name"]
    profile_dir = Path(config["profile_dir"])

    if not mx_token:
        print("[!] No Matrix access token — cannot connect to dashboard")
        return

    if not mx_room:
        print("[!] No Matrix room — cannot connect to dashboard")
        return

    print(f"[*] Matrix adapter starting: {mx_user} → {mx_room}")

    sync_url = f"{MATRIX_BASE}/client/v3/sync"
    send_url = f"{MATRIX_BASE}/client/v3/rooms/{mx_room}/send/m.room.message"
    headers = {
        "Authorization": f"Bearer {mx_token}",
        "Content-Type": "application/json",
    }

    since = None
    running = True

    async with aiohttp.ClientSession() as session:
        # Send online presence
        try:
            await session.put(
                f"{MATRIX_BASE}/client/v3/presence/{mx_user}/status",
                headers=headers,
                json={"presence": "online", "status_msg": "Sovereign agent — awake and listening"},
            )
            print("[+] Presence: online")
        except Exception as e:
            print(f"[!] Presence update failed: {e}")

        # Send a "ready" message to the room
        try:
            await session.put(
                send_url + f"/{int(time.time() * 1000)}",
                headers=headers,
                json={
                    "msgtype": "m.notice",
                    "body": f"🟢 {agent_name} is now online and ready.",
                },
            )
            print(f"[+] Ready message sent to room")
        except Exception as e:
            print(f"[!] Ready message failed: {e}")

        while running:
            try:
                params = {"timeout": 30000, "filter": '{"room":{"timeline":{"limit":10}}}'}
                if since:
                    params["since"] = since

                async with session.get(sync_url, headers=headers, params=params, timeout=35) as resp:
                    if resp.status != 200:
                        print(f"[!] Sync error: {resp.status}")
                        await asyncio.sleep(POLL_INTERVAL)
                        continue

                    data = await resp.json()
                    since = data.get("next_batch", since)

                    # Process room events
                    rooms = data.get("rooms", {}).get("join", {})
                    for rid, room_data in rooms.items():
                        timeline = room_data.get("timeline", {}).get("events", [])
                        for event in timeline:
                            if event.get("sender") == mx_user:
                                continue  # skip own messages
                            if event.get("type") != "m.room.message":
                                continue

                            content = event.get("content", {})
                            body = content.get("body", "")
                            sender = event.get("sender", "unknown")

                            if body.strip():
                                print(f"[msg] {sender}: {body[:100]}")

                                # Write to agent inbox
                                inbox = profile_dir / "state" / "dashboard_inbox.jsonl"
                                inbox.parent.mkdir(parents=True, exist_ok=True)
                                with open(inbox, "a") as f:
                                    f.write(json.dumps({
                                        "sender": sender,
                                        "content": body,
                                        "room_id": rid,
                                        "event_id": event.get("event_id", ""),
                                        "timestamp": event.get("origin_server_ts", time.time() * 1000),
                                    }) + "\n")

            except asyncio.CancelledError:
                running = False
                break
            except Exception as e:
                print(f"[!] Sync error: {e}")
                await asyncio.sleep(POLL_INTERVAL)

    print(f"[*] Matrix adapter stopped for {agent_name}")


async def send_matrix_message(config: dict, content: str):
    """Send a message to the agent's Matrix room."""
    mx_token = config["mx_token"]
    mx_room = config["mx_room"]

    if not mx_token or not mx_room:
        return

    send_url = f"{MATRIX_BASE}/client/v3/rooms/{mx_room}/send/m.room.message"
    headers = {
        "Authorization": f"Bearer {mx_token}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        await session.put(
            send_url + f"/{int(time.time() * 1000)}",
            headers=headers,
            json={
                "msgtype": "m.text",
                "body": content,
            },
        )


def main():
    parser = argparse.ArgumentParser(description="CEM888 Dashboard Matrix Adapter")
    parser.add_argument("--profile", "-p", required=True, help="Agent profile name")
    parser.add_argument("--send", "-s", help="Send a single message and exit")
    args = parser.parse_args()

    config = load_config(args.profile)

    if args.send:
        asyncio.run(send_matrix_message(config, args.send))
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def shutdown():
            print("\n[*] Shutting down...")
            for task in asyncio.all_tasks(loop):
                task.cancel()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, shutdown)
            except NotImplementedError:
                pass

        try:
            loop.run_until_complete(matrix_sync_loop(config))
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()


if __name__ == "__main__":
    main()
