from .general import get_domain_name, create_project_dirs
from .LinkFinder import crawler
from .scraper import scraper
import argparse


def worker(url, max):
    domain_name = get_domain_name(url)
    create_project_dirs(domain_name)

    links_path = crawler(url, max)
    layout_path = f'{domain_name}/tags/'

    scraper(links_path, layout_path)

    return layout_path