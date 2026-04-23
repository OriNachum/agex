import json

from typer.testing import CliRunner

from agent_experience.cli import app


def test_explain_agex_prints_self_describing_page():
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "agex"])
    assert result.exit_code == 0
    assert "agex" in result.stdout
    assert "overview" in result.stdout
    assert "learn" in result.stdout


def test_explain_explain_reads_command_skill_md():
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "explain"])
    assert result.exit_code == 0
    assert "agex explain" in result.stdout.lower()


def test_explain_unknown_topic_exits_1_with_menu():
    """Unknown topic → exit 1 (user error per afi contract)."""
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "unknown-topic-xyz"])
    assert result.exit_code == 1
    assert "unknown" in result.stderr.lower()


def test_explain_rejects_path_traversal():
    runner = CliRunner()
    for bad in ("../../../etc/passwd", "/etc/passwd", "..", "a/b", "learn/introspect"):
        result = runner.invoke(app, ["explain", bad])
        assert result.exit_code == 1, f"expected exit 1 for topic={bad!r}"


# ---------------------------------------------------------------------------
# Path-list (explain [path...]) — afi contract item 2
# ---------------------------------------------------------------------------


def test_explain_no_args_returns_root():
    """``agex explain`` (no topic) shows the agex root page."""
    runner = CliRunner()
    result = runner.invoke(app, ["explain"])
    assert result.exit_code == 0
    assert "agex" in result.stdout
    assert "overview" in result.stdout


def test_explain_single_path_matches_flat_topic():
    """``agex explain overview`` resolves to the overview SKILL.md."""
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "overview"])
    assert result.exit_code == 0
    assert "overview" in result.stdout.lower()


def test_explain_multi_path_uses_first_element():
    """``agex explain hook write`` uses 'hook' as the topic (flat tree)."""
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "hook", "write"])
    assert result.exit_code == 0
    assert "hook" in result.stdout.lower()


# ---------------------------------------------------------------------------
# --json — afi contract item 3
# ---------------------------------------------------------------------------


def test_explain_json_envelope():
    """``agex explain --json agex`` wraps markdown in a JSON envelope."""
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "--json", "agex"])
    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert envelope["command"] == "explain"
    assert envelope["topic"] == "agex"
    assert envelope["format"] == "markdown"
    assert envelope["exit_code"] == 0
    assert "agex_version" in envelope
    assert len(envelope["content"]) > 0


def test_explain_json_error():
    """``agex explain --json bad-topic`` returns JSON on stdout + stderr."""
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "--json", "no-such-topic-xyz"])
    assert result.exit_code == 1
    # stdout still has JSON envelope with exit_code != 0
    envelope = json.loads(result.stdout)
    assert envelope["exit_code"] == 1
    assert envelope["command"] == "explain"
    # stderr has structured error
    error_obj = json.loads(result.stderr)
    assert error_obj["code"] == 1
    assert "message" in error_obj
    assert "remediation" in error_obj


def test_explain_json_no_args_returns_root():
    """``agex explain --json`` returns root page in JSON envelope."""
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "--json"])
    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert envelope["topic"] == "agex"
    assert envelope["exit_code"] == 0
