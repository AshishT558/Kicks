import scrapy
import pandas as pd
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import defer, reactor
from items import ShoeProduct
from custom_selenium_middleware import CustomSeleniumMiddleware
# Selenium imports
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

Skechers_items = []
Skechers_df = pd.DataFrame()

class SkechersSpider(scrapy.Spider):
    name = 'SkechersSpider'
    shoe_name = "cali breeze"
    start_urls = [f"https://www.skechers.com/search/?q={shoe_name}"]

    def parse(self, response):
        product_selector = "div.product"
        products = response.css(product_selector)

        for product in products:
            item = ShoeProduct()
            try:
                # Get Gender
                gender_tag = product.css('div.c-product-tile__gender::text').get().strip()
                if "women's" in gender_tag.casefold():
                    gender = "Women"
                elif "men's" in gender_tag.casefold():
                    gender = "Men"
                elif "boys'" in gender_tag.casefold():
                    gender = "Kids"
                elif "girls'" in gender_tag.casefold():
                    gender = "Kids"
                else:
                    gender = "Unisex"

                # Check for sales price vs price range vs single price
                span_values = product.css('span.value::attr(content)')
                span_sales = product.css('span.sales')

                if len(span_values) == 1:
                    original_price = span_values[0].get()
                    sale_price = original_price
                elif len(span_values) == 2:
                    if len(span_sales) == 1:
                        original_price = span_values[0].get()
                        sale_price = span_values[1].get()
                    elif len(span_sales) == 2:
                        original_price = span_values[0].get()
                        sale_price = original_price

                item['name'] = product.css('a.link.c-product-tile__title::text').get().strip()
                item['link'] = "https://www.skechers.com" + product.css('a.link.c-product-tile__title').attrib['href']
                item['image'] = product.css('img.tile-image.c-product-tile__img').attrib['src']
                item['original_price'] = original_price
                item['sale_price'] = sale_price
                item['gender'] = gender

            except Exception as e:
                item['name'] = "No Data"
                item['link'] = "No Data"
                item['image'] = "No Data"
                item['original_price'] = "No Data"
                item['sale_price'] = "No Data"
                item['gender'] = "No Data"

            Skechers_items.append(item)

        next_page = response.css('a.btn.btn-redesign.btn-primary-ghost.btn-md.col-12.col-sm-4::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
        else:
            self.logger.info("No more pages found")

    def closed(self, reason):
        global Skechers_df
        Skechers_df = pd.DataFrame(Skechers_items, columns=ShoeProduct.fields)

underarmour_items = []
underarmour_df = pd.DataFrame()

class UnderArmourSpider(scrapy.Spider):
    name = 'UnderArmourSpider'
    shoe_name = "Unisex UA Fat Tire Venture Pro Shoes"
    start_urls = [f"https://www.underarmour.com/en-us/search/?q={shoe_name}"]

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=5,
                wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.false.ProductTile_product-tile-container__flx2K.module__primary-img.false.ProductTile_split-view-enabled__eCRsC"))
            )

    def parse(self, response):
        product_selector = "div.false.ProductTile_product-tile-container__flx2K.module__primary-img.false.ProductTile_split-view-enabled__eCRsC"
        products = response.css(product_selector)

        for product in products:
            item = ShoeProduct()
            try:
                title = product.css('a.ProductTile_product-item-link__tSc19::text').get()
                if "women's" in title.casefold():
                    gender = "Women"
                elif "men's" in title.casefold():
                    gender = "Men"
                elif "boy's" in title.casefold():
                    gender = "Kids"
                elif "girl's" in title.casefold():
                    gender = "Kids"
                else:
                    gender = "Unisex"

                item_sale_element = product.css('span.bfx-price.bfx-sale-price::text').get()
                regular_price = product.css('span.bfx-price.bfx-list-price::text').get().replace('$', '')
                if item_sale_element is not None:
                    sales_price = item_sale_element.replace('$', '')
                else:
                    sales_price = regular_price

                item['name'] = title
                item['link'] = product.css('a.ProductTile_product-item-link__tSc19').attrib['href']
                item['image'] = product.css('img.Image_responsive_image__Hsr2N').attrib['src']
                item['original_price'] = regular_price
                item['sale_price'] = sales_price
                item['gender'] = gender

            except Exception as e:
                item['name'] = 'No Data'
                item['link'] = 'No Data'
                item['image'] = 'No Data'
                item['original_price'] = 'No Data'
                item['sale_price'] = 'No Data'
                item['gender'] = 'No Data'

            underarmour_items.append(item)

        next_page = response.css('a[aria-label="Go to the next page"]::attr(href)').get()
        if next_page:
            next_page_url = 'https://www.underarmour.com' + next_page
            yield SeleniumRequest(
                url=next_page_url,
                callback=self.parse,
                wait_time=5,
                wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.false.ProductTile_product-tile-container__flx2K.module__primary-img.false.ProductTile_split-view-enabled__eCRsC"))
            )
        else:
            self.logger.info("No more pages found")

    def closed(self, reason):
        global underarmour_df
        underarmour_df = pd.DataFrame(underarmour_items, columns=ShoeProduct.fields)

# Setup logging and runner
configure_logging()
runner = CrawlerRunner(settings={
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

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(SkechersSpider)
    yield runner.crawl(UnderArmourSpider)
    reactor.stop()

crawl()
reactor.run()  # the script will block here until the last crawl call is finished

# Combine dataframes
frames = [Skechers_df, underarmour_df]
df_merged = pd.concat(frames, ignore_index=True, sort=False)
print(df_merged)
