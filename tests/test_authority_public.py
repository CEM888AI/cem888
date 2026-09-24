from pathlib import Path

import pytest

from agent.authority import AgentAuthority


def _authority(tmp_path: Path) -> AgentAuthority:
    profile = tmp_path / "profiles" / "cem"
    allowed = profile / "allowed"
    protected = tmp_path / "protected"
    forbidden = tmp_path / "forbidden"
    manifest = profile / "authority.json"
    for path in (profile, allowed, protected, forbidden):
        path.mkdir(parents=True, exist_ok=True)
    manifest.write_text("{}", encoding="utf-8")
    return AgentAuthority(
        schema_version=1,
        agent_id="cem",
        display_name="CEM",
        aliases=("cem",),
        host_id="local",
        runtime_service="cem888",
        profile_name="cem",
        profile_root=profile,
        profile_source_repo="cem888-config",
        profile_source_remote="local",
        profile_deploy_target="local",
        shared_core_source_repo="cem888",
        shared_core_runtime_root=str(tmp_path),
        allowed_write_roots=(allowed,),
        protected_write_roots=(protected, allowed, forbidden),
        forbidden_write_roots=(forbidden,),
        sanctioned_deploy_routes=("approved-route",),
        manifest_path=manifest,
        manifest_revision="test",
    )


def test_authority_manifest_is_immutable(tmp_path: Path) -> None:
    authority = _authority(tmp_path)
    denial = authority.write_denial(authority.manifest_path)
    assert denial is not None
    assert "AUTHORITY_MANIFEST_IMMUTABLE" in denial


def test_forbidden_root_is_denied(tmp_path: Path) -> None:
    authority = _authority(tmp_path)
    target = authority.forbidden_write_roots[0] / "state.json"
    denial = authority.write_denial(target)
    assert denial is not None
    assert "TARGET_AUTHORITY_MISMATCH" in denial


def test_allowed_root_inside_protected_space_is_allowed(tmp_path: Path) -> None:
    authority = _authority(tmp_path)
    target = authority.allowed_write_roots[0] / "state.json"
    assert authority.write_denial(target) is None


def test_unprotected_path_is_outside_tier_zero_scope(tmp_path: Path) -> None:
    authority = _authority(tmp_path)
    target = tmp_path / "ordinary-user-file.txt"
    assert authority.write_denial(target) is None


def test_terminal_mutation_of_forbidden_literal_path_is_denied(tmp_path: Path) -> None:
    authority = _authority(tmp_path)
    target = authority.forbidden_write_roots[0] / "state.json"
    denial = authority.command_denial(f"rm -f {target}")
    assert denial is not None
    assert "TARGET_AUTHORITY_MISMATCH" in denial


def test_terminal_read_is_not_reclassified_as_mutation(tmp_path: Path) -> None:
    authority = _authority(tmp_path)
    target = authority.forbidden_write_roots[0] / "state.json"
    assert authority.command_denial(f"cat {target}") is None
