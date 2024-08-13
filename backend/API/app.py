import crochet
crochet.setup()  # initialize crochet before further imports

from flask import Flask, jsonify
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher

from custom_selenium_middleware import CustomSeleniumMiddleware
from spiders.UnderArmourSpider import UnderArmourSpider
from spiders.SkechersSpider import SkechersSpider
from spiders.AdidasSpider import AdidasSpider
from spiders.NikeSpider import NikeSpider

import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz

app = Flask(__name__)

output_data = []

crawl_runner = CrawlerRunner(settings={
    'SELENIUM_DRIVER_NAME': 'firefox',
    'SELENIUM_DRIVER_ARGUMENTS': ['--headless'], 
    'SELENIUM_DRIVER_EXECUTABLE_PATH': 'geckodriver',
    'DOWNLOADER_MIDDLEWARES': {
        CustomSeleniumMiddleware: 800

    },
    'LOG_LEVEL': 'INFO',
})

@app.before_request
def setup():
    output_data.clear()

@app.route("/")
def welcome():
    return "Test Env"


@app.route("/scrape/<string:shoe_arg>/")
def scrape(shoe_arg):

    print("data length pre-run:{}".format(len(output_data)))
    # run crawler in twisted reactor synchronously
    scrape_with_crochet(UnderArmourSpider, shoe_arg)
    scrape_with_crochet(SkechersSpider, shoe_arg)
    scrape_with_crochet(AdidasSpider, shoe_arg)
    scrape_with_crochet(NikeSpider, shoe_arg)
    
    # Scoring stuff here
    #
    #

    print("data length post-run:{}".format(len(output_data)))

    df = pd.DataFrame(output_data)
    df['Retrieval Date'] = datetime.now()

    def score(shoe_name):
        return fuzz.partial_ratio(shoe_arg, shoe_name)

    df['Score'] = df['name'].apply(score)
    return jsonify(df.to_dict(orient='records'))


@crochet.wait_for(timeout=120.0)
def scrape_with_crochet(spider_name, shoe_arg):
    # signal fires when single item is processed
    # and calls _crawler_result to append that item
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(spider_name, shoe_arg)
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