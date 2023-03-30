import click

from versions.meta import python_version_info, version_info

NAME = "versions"
PYTHON = "python"

WITH_NAME = "{} {}"
with_name = WITH_NAME.format


@click.help_option("--help", "-h")
@click.option("--raw", "-r", is_flag=True, default=False)
@click.option("--python", "-p", is_flag=True, default=False)
@click.option("--normal", "-n", is_flag=True, default=False)
@click.command(name=NAME)
def versions(raw: bool, python: bool, normal: bool) -> None:
    version, name = (python_version_info, PYTHON) if python else (version_info, NAME)

    string = version.to_pep440_string() if normal else version.to_string()

    if not raw:
        string = with_name(name, string)

    click.echo(string)
