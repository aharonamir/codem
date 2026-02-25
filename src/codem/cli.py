import typer

app = typer.Typer(help="Codem – a terminal-first deterministic AI coding agent.")


@app.command()
def run(task: str = typer.Argument(help="Task description for the agent to execute")):
    """Run a coding task."""
    typer.echo(f"Task received: {task}")


@app.command()
def init():
    """Initialize a codem project in the current directory."""
    typer.echo("Not implemented")


@app.command()
def plan():
    """Generate an execution plan for a task."""
    typer.echo("Not implemented")


@app.command()
def execute():
    """Execute a previously generated plan."""
    typer.echo("Not implemented")


@app.command()
def rollback():
    """Rollback the last executed plan."""
    typer.echo("Not implemented")


@app.command()
def doctor():
    """Check environment and configuration health."""
    typer.echo("Not implemented")
