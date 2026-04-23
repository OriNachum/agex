"""Tests for unknown-command routing, CLI entry-point behaviour, and main().

The subprocess tests exercise the real argv path end-to-end; the in-process
tests call main() / _main_entrypoint directly for coverage.

Exit-code convention (afi agent-first CLI contract, 0.14.0+):
  0 = success, 1 = user error, 2 = env/setup or usage error.
"""

import subprocess
import sys

import pytest

from agent_experience.cli import _KNOWN_COMMANDS, _main_entrypoint, main


# ---------------------------------------------------------------------------
# Subprocess tests (end-to-end through __main__.py → _main_entrypoint)
# ---------------------------------------------------------------------------


def test_unknown_command_exits_1(tmp_path):
    """An unknown subcommand prints agex explain agex to stdout and exits 1."""
    result = subprocess.run(
        [sys.executable, "-m", "agent_experience", "frobnicate"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 1
    assert "agex" in result.stdout
    assert "overview" in result.stdout
    assert "unknown command" in result.stderr.lower()


def test_known_command_still_works(tmp_path):
    """A known command (explain agex) still routes correctly and exits 0."""
    result = subprocess.run(
        [sys.executable, "-m", "agent_experience", "explain", "agex"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0
    assert "agex" in result.stdout


def test_version_flag_still_works(tmp_path):
    """The --version flag bypasses the unknown-command handler and exits 0."""
    result = subprocess.run(
        [sys.executable, "-m", "agent_experience", "--version"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode == 0
    # Version string is a non-empty line on stdout
    assert result.stdout.strip() != ""


def test_zero_args_shows_help(tmp_path):
    """Invoking agex with no arguments triggers the Typer help path."""
    result = subprocess.run(
        [sys.executable, "-m", "agent_experience"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    combined = result.stdout + result.stderr
    # Exit code may be 0 (help shown) or 2 (usage error) depending on
    # Click/Typer version — both are acceptable. The key assertion is that
    # help text is displayed.
    assert result.returncode in (0, 2)
    assert "Usage:" in combined or "usage:" in combined.lower()


# ---------------------------------------------------------------------------
# In-process tests for main(argv) → int  (the afi contract entry point)
# ---------------------------------------------------------------------------


def test_main_unknown_command_returns_1(capsys):
    """main() returns 1 for an unknown subcommand."""
    rc = main(["frobnicate"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "unknown command 'frobnicate'" in captured.err
    assert "overview" in captured.out  # body of agex explain agex


def test_main_known_command_returns_0(capsys):
    """main(['explain', 'agex']) returns 0."""
    rc = main(["explain", "agex"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "agex" in captured.out


def test_main_version_returns_0(capsys):
    """main(['--version']) returns 0 (exit via click.Exit, not SystemExit)."""
    rc = main(["--version"])
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out.strip() != ""


def test_main_no_args_returns_0_or_2(capsys):
    """main([]) shows help and returns 0 or 2 (depends on Click version)."""
    rc = main([])
    assert rc in (0, 2)


def test_main_returns_int():
    """main() always returns an int, not None."""
    rc = main(["explain", "agex"])
    assert isinstance(rc, int)


# ---------------------------------------------------------------------------
# Legacy _main_entrypoint tests (coverage for the thin wrapper)
# ---------------------------------------------------------------------------


def test_main_entrypoint_unknown_command_exits_1(monkeypatch, capsys):
    """Direct invocation: unknown argv[0] triggers the return-1 branch."""
    monkeypatch.setattr(sys, "argv", ["agex", "frobnicate"])
    with pytest.raises(SystemExit) as excinfo:
        _main_entrypoint()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "unknown command 'frobnicate'" in captured.err
    assert "overview" in captured.out  # body of agex explain agex


def test_main_entrypoint_delegates_to_main(monkeypatch):
    """_main_entrypoint calls main() and sys.exit's with the result."""
    monkeypatch.setattr(sys, "argv", ["agex", "explain", "agex"])
    with pytest.raises(SystemExit) as excinfo:
        _main_entrypoint()
    assert excinfo.value.code == 0


def test_known_commands_set_matches_registered_app_commands():
    """Guard: _KNOWN_COMMANDS must stay in sync with Typer's registered
    top-level commands (per the maintenance comment in cli.py)."""
    from agent_experience.cli import app, hook_app  # noqa: F401

    registered = {cmd.name for cmd in app.registered_commands}
    registered |= {grp.name for grp in app.registered_groups}
    assert _KNOWN_COMMANDS == registered


def test_dunder_main_module_imports_cleanly():
    """Exercise agent_experience/__main__.py so its top-level imports and
    ``if __name__ == '__main__'`` guard are observed by the coverage tracker."""
    import importlib

    module = importlib.import_module("agent_experience.__main__")
    # The module must re-export the real entry point.
    assert module._main_entrypoint is _main_entrypoint
    assert module.main is main
