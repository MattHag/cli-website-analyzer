import click
from loguru import logger

from website_checker.main import WebsiteChecker

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("url")
@click.option("-p", "--max-pages", type=int, help="Crawl a maximum of n pages")
@click.option("-s", "--save", is_flag=True, help="Save the report to a file")
def main(url, max_pages, save):
    click.echo("Given URL is: '%s'" % url)
    if max_pages:
        logger.debug("Crawl up to %d pages" % max_pages)
    WebsiteChecker(max_pages=max_pages, save_crawled_pages=save).check(url)


if __name__ == "__main__":
    main()
