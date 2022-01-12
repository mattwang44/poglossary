import typer


def log_error(msg, err=True):
    msg = typer.style(msg, fg=typer.colors.RED, bold=True)
    typer.echo(msg, err=err)
    raise typer.Exit(code=1)


def log_info(msg):
    msg = typer.style(msg, fg=typer.colors.GREEN)
    typer.echo(msg)
