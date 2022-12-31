import click


@click.command()
@click.argument("url")
def cli(url):
    click.echo("Given URL is: '%s'" % url)


if __name__ == "__main__":
    cli()
