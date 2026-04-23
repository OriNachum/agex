import json

from typer.testing import CliRunner

from agent_experience.cli import app


def test_learn_menu_lists_introspect():
    runner = CliRunner()
    result = runner.invoke(app, ["learn", "--agent", "claude-code"])
    assert result.exit_code == 0
    assert "introspect" in result.stdout


def test_learn_introspect_emits_lesson_and_template():
    runner = CliRunner()
    result = runner.invoke(app, ["learn", "introspect", "--agent", "claude-code"])
    assert result.exit_code == 0
    assert "build an `introspect` skill" in result.stdout
    # Template body embedded as code block
    assert "Audit the current project" in result.stdout


def test_learn_unknown_topic_exits_1():
    """Unknown topic → exit 1 (user error per afi contract)."""
    runner = CliRunner()
    result = runner.invoke(app, ["learn", "xyz", "--agent", "claude-code"])
    assert result.exit_code == 1
    assert "unknown topic" in result.stderr.lower()
    assert "introspect" in result.stdout  # menu in stdout


def test_learn_rejects_path_traversal():
    runner = CliRunner()
    for bad in ("../../../etc/passwd", "/etc/passwd", "..", "a/b", "INTROSPECT"):
        result = runner.invoke(app, ["learn", bad, "--agent", "claude-code"])
        assert result.exit_code == 1, f"expected exit 1 for topic={bad!r}"
        assert "unknown topic" in result.stderr.lower()


def test_learn_menu_lists_all_v01_topics():
    runner = CliRunner()
    result = runner.invoke(app, ["learn", "--agent", "claude-code"])
    for topic in ("introspect", "visualize", "gamify", "levelup"):
        assert topic in result.stdout


def test_learn_visualize_emits_lesson():
    runner = CliRunner()
    result = runner.invoke(app, ["learn", "visualize", "--agent", "claude-code"])
    assert result.exit_code == 0
    assert "visualize" in result.stdout.lower()


def test_learn_gamify_includes_levelup_template():
    runner = CliRunner()
    result = runner.invoke(app, ["learn", "gamify", "--agent", "claude-code"])
    assert result.exit_code == 0
    assert "gamify" in result.stdout
    assert "levelup" in result.stdout


# ---------------------------------------------------------------------------
# --json — afi contract item 3
# ---------------------------------------------------------------------------


def test_learn_json_menu():
    """``agex learn --json --agent claude-code`` wraps menu in JSON."""
    runner = CliRunner()
    result = runner.invoke(app, ["learn", "--json", "--agent", "claude-code"])
    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert envelope["command"] == "learn"
    assert envelope["agent"] == "claude-code"
    assert envelope["format"] == "markdown"
    assert envelope["exit_code"] == 0
    assert "introspect" in envelope["content"]


def test_learn_json_topic():
    """``agex learn --json introspect --agent claude-code`` wraps lesson."""
    runner = CliRunner()
    result = runner.invoke(
        app, ["learn", "--json", "introspect", "--agent", "claude-code"]
    )
    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert envelope["topic"] == "introspect"
    assert "introspect" in envelope["content"].lower()


def test_learn_json_invalid_agent():
    """Invalid backend with --json emits structured error on stderr."""
    runner = CliRunner()
    result = runner.invoke(app, ["learn", "--json", "--agent", "gemini"])
    assert result.exit_code == 1
    error_obj = json.loads(result.stderr)
    assert error_obj["code"] == 1
    assert "gemini" in error_obj["message"]
    assert "remediation" in error_obj


def test_learn_json_unknown_topic():
    """Unknown topic with --json emits JSON envelope + structured error."""
    runner = CliRunner()
    result = runner.invoke(
        app, ["learn", "--json", "no-such-xyz", "--agent", "claude-code"]
    )
    assert result.exit_code == 1
    envelope = json.loads(result.stdout)
    assert envelope["exit_code"] == 1
    error_obj = json.loads(result.stderr)
    assert error_obj["code"] == 1
