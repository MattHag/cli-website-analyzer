import click
from loguru import logger

from website_checker.analyze.analyzer import Analyzer
from website_checker.analyze.result import adapter
from website_checker.main import run_full_analysis

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
    analyzer = Analyzer()
    pdf_path, _, _ = run_full_analysis(
        url,
        analyzer,
        converter=adapter,
        rate_limit=rate_limit,
        max_pages=max_pages,
        save_crawled_pages=save,
    )
    click.echo("Report saved to file://%s" % pdf_path)


if __name__ == "__main__":
    main()
