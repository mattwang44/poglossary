import typer


def error(msg, err=False):
    msg = typer.style(msg, fg=typer.colors.RED, bold=True)
    typer.echo(msg, err=err)
    raise typer.Exit(code=1)


def info(msg):
    msg = typer.style(msg, fg=typer.colors.GREEN)
    typer.echo(msg)
