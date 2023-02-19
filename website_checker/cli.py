import click
from loguru import logger

from website_checker.main import WebsiteChecker


@click.command()
@click.argument("url")
@click.option("-p", "--max-pages", type=int, help="Crawl a maximum of n pages")
def main(url, max_pages):
    click.echo("Given URL is: '%s'" % url)
    if max_pages:
        logger.debug("Crawl up to %d pages" % max_pages)
    WebsiteChecker(max_pages=max_pages).check(url)


if __name__ == "__main__":
    main()
