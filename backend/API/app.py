import crochet
crochet.setup()  # initialize crochet before further imports

from flask import Flask, jsonify
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher

from custom_selenium_middleware import CustomSeleniumMiddleware
from UnderArmourSpider import UnderArmourSpider
from SkechersSpider import SkechersSpider


app = Flask(__name__)
output_data = []
crawl_runner = CrawlerRunner(settings={
    'SELENIUM_DRIVER_NAME': 'firefox',
    'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],  # Optional: Headless mode
    'SELENIUM_DRIVER_EXECUTABLE_PATH': '/Users/adic/Desktop/CODE/Kicks/backend/ResellersScraper/ResellersScraper/spiders/geckodriver',
    'DOWNLOADER_MIDDLEWARES': {
        CustomSeleniumMiddleware: 800

    },
    'FEEDS': {
        'backend/ResellersScraper/UA-results.json': {
            'format': 'json',
            'encoding': 'utf8',
            'store_empty': False,
            'indent': 4,
            'overwrite': True,
        },
    },
    'LOG_LEVEL': 'INFO',
})
# crawl_runner = CrawlerRunner(get_project_settings()) if you want to apply settings.py

@app.route("/")
def welcome():
    return "Test Env"


@app.route("/scrape")
def scrape():
    # run crawler in twisted reactor synchronously
    scrape_with_crochet(UnderArmourSpider)
    scrape_with_crochet(SkechersSpider)

    return jsonify(output_data)


@crochet.wait_for(timeout=60.0)
def scrape_with_crochet(spider_name):
    # signal fires when single item is processed
    # and calls _crawler_result to append that item
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(spider_name)
    return eventual  # returns a twisted.internet.defer.Deferred


def _crawler_result(item, response, spider):
    """
    We're using dict() to decode the items.
    Ideally this should be done using a proper export pipeline.
    """
    output_data.append(dict(item))


if __name__=='__main__':
    # pretty print
    app.json_provider_class.compact = False
    #run on local server
    app.run('0.0.0.0', 8080)