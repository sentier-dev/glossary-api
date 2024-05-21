"""Shell utils for dds_glossary."""

from invoke import task
from invoke.context import Context


@task
def clean(
    ctx: Context,
    bytecode: bool = False,
    pytest: bool = False,
    mypy: bool = False,
    extra: str = "",
) -> None:
    """
    Clean up the project directory.

    Args:
        ctx: The Invoke context.
        bytecode: Whether to clean up compiled Python files.
        pytest: Whether to clean up pytest cache and coverage files.
        mypy: Whether to clean up mypy cache files.
        extra: Additional directories or files to clean up.
    """
    patterns = ["build", "dist", "*.egg-info"]
    if bytecode:
        patterns.append("**/*.pyc")
    if pytest:
        patterns.extend([".pytest_cache", ".coverage"])
    if mypy:
        patterns.append(".mypy_cache")
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        ctx.run(f"rm -rf {pattern}", hide=True, warn=True)


@task
def install(
    ctx: Context,
    editable: bool = False,
    testing: bool = False,
    dev: bool = False,
    report: bool = False,
) -> None:
    """
    Install the project in editable mode.

    Args:
        ctx: The Invoke context.
        editable: Whether to install in editable mode.
        testing: Whether to install test dependencies.
        dev: Whether to install development dependencies.
        report: If report, show the command output.
    """
    command = "pip install ."
    if editable:
        command += " -e"

    deps: list[str] = []
    if testing:
        deps.append("test")
    if dev:
        deps.append("dev")
    if deps:
        command += f"[{','.join(deps)}]"

    hide = not report
    result = ctx.run(command, hide=hide, warn=True)
    if hide and result:
        print(result.stdout.splitlines()[-1])


@task
def precommit(ctx: Context) -> None:
    """
    Run pre-commit checks.

    Args:
        ctx: The Invoke context.
    """
    ctx.run("pre-commit run --all-files", warn=True)


@task
def test(
    ctx: Context,
    integration: bool = False,
    report: bool = False,
) -> None:
    """
    Run unit and integration tests.

    Args:
        ctx: The Invoke context.
        integration: Whether to run integration tests.
        report: If report, show the command output.
    """
    hide = not report

    print("Running unit tests...")
    result = ctx.run("pytest tests/unit", hide=hide, warn=True)
    if hide and result:
        print(result.stdout.splitlines()[-1])

    if integration:
        print("Running integration tests...")
        result = ctx.run("pytest tests/integration", hide=hide, warn=True)
        if hide and result:
            print(result.stdout.splitlines()[-1])
