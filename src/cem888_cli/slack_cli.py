"""``cem888 slack ...`` CLI subcommands.

Today only ``cem888 slack manifest`` is implemented — it generates the
Slack app manifest JSON for registering every gateway command as a native
Slack slash (``/btw``, ``/stop``, ``/model``, …) so users get the same
first-class slash UX Discord and Telegram already have.

Typical workflow::

    $ cem888 slack manifest > slack-manifest.json
    # or:
    $ cem888 slack manifest --write

Then paste the printed JSON into the Slack app config (Features → App
Manifest → Edit) and click Save. Slack diffs the manifest and prompts
for reinstall when scopes/commands change.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _build_full_manifest(bot_name: str, bot_description: str) -> dict:
    """Build a full Slack manifest merging display info + our slash list.

    The slash-command list is always generated from ``COMMAND_REGISTRY`` so
    it stays in sync with the rest of CEM888. Other manifest sections
    (display info, OAuth scopes, socket mode) are set to sensible defaults
    for a CEM888 deployment — users can tweak them in the Slack UI after
    pasting.
    """
    from cem888_cli.commands import slack_app_manifest

    partial = slack_app_manifest()
    slashes = partial["features"]["slash_commands"]

    return {
        "_metadata": {
            "major_version": 1,
            "minor_version": 1,
        },
        "display_information": {
            "name": bot_name[:35],
            "description": (bot_description or "Your CEM888 agent on Slack")[:140],
            "background_color": "#1a1a2e",
        },
        "features": {
            "app_home": {
                "home_tab_enabled": False,
                "messages_tab_enabled": True,
                "messages_tab_read_only_enabled": False,
            },
            "bot_user": {
                "display_name": bot_name[:80],
                "always_online": True,
            },
            "slash_commands": slashes,
            "assistant_view": {
                "assistant_description": "Chat with CEM888 in threads and DMs.",
            },
        },
        "oauth_config": {
            "scopes": {
                "bot": [
                    "app_mentions:read",
                    "assistant:write",
                    "channels:history",
                    "channels:read",
                    "chat:write",
                    "commands",
                    "files:read",
                    "files:write",
                    "groups:history",
                    "groups:read",
                    "im:history",
                    "im:read",
                    "im:write",
                    "users:read",
                ],
            },
        },
        "settings": {
            "event_subscriptions": {
                "bot_events": [
                    "app_mention",
                    "assistant_thread_context_changed",
                    "assistant_thread_started",
                    "message.channels",
                    "message.groups",
                    "message.im",
                ],
            },
            "interactivity": {
                "is_enabled": True,
            },
            "org_deploy_enabled": False,
            "socket_mode_enabled": True,
            "token_rotation_enabled": False,
        },
    }


def slack_manifest_command(args) -> int:
    """Print or write a Slack app manifest JSON.

    Flags (all parsed in ``cem888_cli/main.py``):
      --write [PATH]  Write to file instead of stdout (default path:
                      ``$CEM888_HOME/slack-manifest.json``)
      --name NAME     Override the bot display name (default: "CEM888")
      --description DESC  Override the bot description
      --slashes-only  Emit only the ``features.slash_commands`` array (for
                      merging into an existing manifest manually)
    """
    name = getattr(args, "name", None) or "CEM888"
    description = getattr(args, "description", None) or "Your CEM888 agent on Slack"

    if getattr(args, "slashes_only", False):
        from cem888_cli.commands import slack_app_manifest

        manifest = slack_app_manifest()["features"]["slash_commands"]
    else:
        manifest = _build_full_manifest(name, description)

    payload = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

    write_target = getattr(args, "write", None)
    if write_target is not None:
        if isinstance(write_target, bool) and write_target:
            # --write with no value → default location
            try:
                from cem888_constants import get_cem888_home

                target = Path(get_cem888_home()) / "slack-manifest.json"
            except Exception:
                target = Path(os.environ.get("CEM888_HOME") or str(Path.home() / ".cem888")) / "slack-manifest.json"
        else:
            target = Path(write_target).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
        print(f"Slack manifest written to: {target}", file=sys.stderr)
        print(
            "\nNext steps:\n"
            "  1. Open https://api.slack.com/apps and pick your CEM888 app\n"
            "     (or create a new one: Create New App → From an app manifest).\n"
            f"  2. Features → App Manifest → paste the contents of\n"
            f"     {target}\n"
            "  3. Save; Slack will prompt to reinstall the app if scopes or\n"
            "     slash commands changed.\n"
            "  4. Make sure Socket Mode is enabled and you have a bot token\n"
            "     (xoxb-...) and app token (xapp-...) configured via\n"
            "     `cem888 setup`.\n",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(payload)
    return 0
