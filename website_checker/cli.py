import click

from website_checker.main import WebsiteChecker


@click.command()
@click.argument("url")
def main(url):
    click.echo("Given URL is: '%s'" % url)
    WebsiteChecker().check(url)


if __name__ == "__main__":
    main()
