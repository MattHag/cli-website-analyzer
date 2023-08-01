import click
from loguru import logger

from website_checker.main import WebsiteChecker

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("url")
@click.option("-r", "--rate-limit", default=0, type=int, help="Limit crawler to n milliseconds per page")
@click.option("-p", "--max-pages", type=int, help="Crawl a maximum of n pages")
@click.option("-s", "--save", is_flag=True, help="Save the crawled pages to a file")
def main(url, rate_limit, max_pages, save):
    if "://" not in url:
        url = "https://" + url
    click.echo("URL is: '%s'" % url)
    if rate_limit:
        logger.debug("Rate limit set to %d milliseconds" % rate_limit)
    if max_pages:
        logger.debug("Crawl up to %d pages" % max_pages)
    pdf_path = WebsiteChecker(rate_limit=rate_limit, max_pages=max_pages, save_crawled_pages=save).check(url)
    click.echo("Report saved to file://%s" % pdf_path)


if __name__ == "__main__":
    main()
