import json as json_module
import sys
from typing import Any, Optional

import click
import typer

from agent_experience import __version__
from agent_experience.commands.explain.scripts import explain as explain_script
from agent_experience.commands.gamify.scripts import install as gamify_script
from agent_experience.commands.hook.scripts import read as hook_read_script
from agent_experience.commands.hook.scripts import write as hook_write_script
from agent_experience.commands.learn.scripts import learn as learn_script
from agent_experience.commands.overview.scripts import overview as overview_script
from agent_experience.core.backend import parse_backend

app = typer.Typer(
    name="agex",
    help="Agent-operated developer-experience CLI.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def _app_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=_version_callback, is_eager=True
    ),
) -> None:
    """Root callback — exists only to hold the --version option.

    Typer invokes the eager _version_callback before any subcommand
    dispatch; there is nothing else to do at the app level.
    """


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def _emit_result(
    stdout: str,
    exit_code: int,
    stderr: str,
    *,
    json_output: bool = False,
    command: str = "",
    meta: dict[str, Any] | None = None,
) -> None:
    """Write command output to stdout/stderr.

    When *json_output* is False (default), emits raw markdown to stdout and
    a plain ``agex: error: …`` string to stderr — the pre-0.14 behaviour.

    When *json_output* is True, wraps the markdown in a JSON envelope on
    stdout and emits a ``{code, message, remediation}`` object on stderr
    for errors (afi agent-first CLI contract).
    """
    if json_output:
        envelope: dict[str, Any] = {
            "agex_version": __version__,
            "command": command,
        }
        if meta:
            envelope.update(meta)
        envelope["content"] = stdout
        envelope["format"] = "markdown"
        envelope["exit_code"] = exit_code
        typer.echo(json_module.dumps(envelope, indent=2))
        if stderr:
            msg = stderr.removeprefix("agex: error: ")
            error_obj = {
                "code": exit_code,
                "message": msg,
                "remediation": f"Run `agex {command} --help` for usage.",
            }
            typer.echo(json_module.dumps(error_obj), err=True)
    else:
        if stdout:
            typer.echo(stdout, nl=False)
        if stderr:
            typer.echo(stderr, err=True)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command("explain")
def explain_cmd(
    paths: Optional[list[str]] = typer.Argument(
        None, help="Topic path (empty = root)."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON envelope."),
) -> None:
    topic = paths[0] if paths else "agex"
    stdout, exit_code, stderr = explain_script.run(topic)
    _emit_result(
        stdout,
        exit_code,
        stderr,
        json_output=json_output,
        command="explain",
        meta={"topic": topic},
    )


def _agent_option() -> Any:
    return typer.Option(
        ..., "--agent", help="Backend: claude-code, codex, copilot, or acp."
    )


hook_app = typer.Typer(
    help="Write and read agex tracking events.", no_args_is_help=True
)
app.add_typer(hook_app, name="hook")


@hook_app.command("write")
def hook_write(
    event: str = typer.Argument(..., help="Event name (e.g., post-tool-use)."),
    args: list[str] = typer.Argument(None, help="Additional key=value pairs."),
) -> None:
    args = args or []
    _, exit_code, stderr = hook_write_script.run(event, args)
    if stderr:
        typer.echo(stderr, err=True)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


@hook_app.command("read")
def hook_read(agent: str = _agent_option()) -> None:
    try:
        backend = parse_backend(agent)
    except ValueError as e:
        typer.echo(f"agex: error: {e}", err=True)
        raise typer.Exit(code=2)
    stdout, exit_code, stderr = hook_read_script.run(backend)
    if stdout:
        typer.echo(stdout, nl=False)
    if stderr:
        typer.echo(stderr, err=True)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


@app.command("learn")
def learn_cmd(
    topic: Optional[str] = typer.Argument(None, help="Lesson topic (omit for menu)."),
    agent: str = _agent_option(),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON envelope."),
) -> None:
    try:
        backend = parse_backend(agent)
    except ValueError as e:
        if json_output:
            error_obj = {
                "code": 1,
                "message": str(e),
                "remediation": "Valid backends: claude-code, codex, copilot, acp.",
            }
            typer.echo(json_module.dumps(error_obj), err=True)
        else:
            typer.echo(f"agex: error: {e}", err=True)
        raise typer.Exit(code=1)
    if topic is None:
        stdout, exit_code, stderr = learn_script.run_menu(backend)
    else:
        stdout, exit_code, stderr = learn_script.run_topic(topic, backend)
    _emit_result(
        stdout,
        exit_code,
        stderr,
        json_output=json_output,
        command="learn",
        meta={"topic": topic, "agent": backend.value},
    )


@app.command("gamify")
def gamify(
    agent: str = _agent_option(),
    uninstall: bool = typer.Option(False, "--uninstall", help="Reverse gamify."),
) -> None:
    try:
        backend = parse_backend(agent)
    except ValueError as e:
        typer.echo(f"agex: error: {e}", err=True)
        raise typer.Exit(code=2)
    if uninstall:
        stdout, exit_code, stderr = gamify_script.uninstall(backend)
    else:
        stdout, exit_code, stderr = gamify_script.install(backend)
    if stdout:
        typer.echo(stdout, nl=False)
    if stderr:
        typer.echo(stderr, err=True)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


@app.command("overview")
def overview_cmd(
    agent: str = _agent_option(),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON envelope."),
) -> None:
    try:
        backend = parse_backend(agent)
    except ValueError as e:
        if json_output:
            error_obj = {
                "code": 1,
                "message": str(e),
                "remediation": "Valid backends: claude-code, codex, copilot, acp.",
            }
            typer.echo(json_module.dumps(error_obj), err=True)
        else:
            typer.echo(f"agex: error: {e}", err=True)
        raise typer.Exit(code=1)
    stdout, exit_code, stderr = overview_script.run(backend)
    _emit_result(
        stdout,
        exit_code,
        stderr,
        json_output=json_output,
        command="overview",
        meta={"agent": backend.value},
    )


# Keep in sync with the @app.command / app.add_typer registrations above.
# If a new top-level command is added, extend this set so main() stops
# routing it to the unknown-command fallback page.
_KNOWN_COMMANDS = {"explain", "overview", "learn", "gamify", "hook"}


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """In-process entry point — returns exit code, never calls ``sys.exit``.

    Culture's ``_passthrough.py`` helper calls ``main(argv)`` instead of
    shelling out so stdout/stderr can be captured in-process.  The contract
    (afi agent-first CLI, ``agentculture/afi-cli#5``):

    * Returns ``int`` for every normal path (success, user error, usage).
    * ``SystemExit`` may still be raised by ``--help`` / ``--version``
      (standard Click/Typer convention with ``standalone_mode=False``).

    Exit codes: 0 = success, 1 = user error, 2 = env/setup or usage error.
    """
    if argv is None:
        argv = sys.argv[1:]

    # Unknown-command routing: show agex root page + error, exit 1.
    if argv and not argv[0].startswith("-") and argv[0] not in _KNOWN_COMMANDS:
        typer.echo(f"agex: error: unknown command '{argv[0]}'", err=True)
        stdout, _, _ = explain_script.run("agex")
        typer.echo(stdout, nl=False)
        return 1

    try:
        app(args=argv, standalone_mode=False)
        return 0
    except click.exceptions.Exit as e:
        return e.exit_code
    except click.exceptions.Abort:
        return 1
    except click.exceptions.UsageError as e:
        typer.echo(f"Error: {e.format_message()}", err=True)
        return 2


def _main_entrypoint() -> None:
    """Shell entry point (``agex`` console script).

    Thin wrapper around :func:`main` that translates the returned exit code
    to ``sys.exit()``.  ``SystemExit`` from ``--help`` / ``--version``
    propagates unchanged.
    """
    sys.exit(main())
