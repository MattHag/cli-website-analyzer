from dataclasses import dataclass
from typing import Optional

import click
from loguru import logger

from website_checker.analyze.analyzer import Analyzer
from website_checker.analyze.result import adapter
from website_checker.main import run_full_analysis

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@dataclass
class Options:
    rate_limit: Optional[int] = None
    max_pages: Optional[int] = None
    save_pages: Optional[bool] = None


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("url")
@click.option("-r", "--rate-limit", default=0, type=int, help="Limit crawler to n milliseconds per page")
@click.option("-p", "--max-pages", type=int, help="Crawl a maximum of n pages")
@click.option("-s", "--save", is_flag=True, help="Save the crawled pages to a file")
def main(url, rate_limit, max_pages, save):
    options = Options(rate_limit, max_pages, save)

    if "://" not in url:
        url = "https://" + url
    click.echo(f"URL is: '{url}'")
    if options.rate_limit:
        logger.debug(f"Rate limit set to {options.rate_limit} milliseconds")
    if options.max_pages:
        logger.debug(f"Crawl up to {options.max_pages} pages")
    analyzer = Analyzer()
    pdf_path, _, _ = run_full_analysis(
        url,
        analyzer,
        converter=adapter,
        options=options,
    )
    click.echo("Report saved to file://%s" % pdf_path)


if __name__ == "__main__":
    main()
