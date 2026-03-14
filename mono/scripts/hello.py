import click


@click.command()
@click.option("--name", default="World", help="Name to greet.")
def main(name: str) -> None:
    """Hello World script — placeholder for one-time scripts."""
    click.echo(f"Hello, {name}!")


if __name__ == "__main__":
    main()
