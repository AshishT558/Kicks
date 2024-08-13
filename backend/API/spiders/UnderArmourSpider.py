import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from items import ShoeProduct
from custom_selenium_middleware import CustomSeleniumMiddleware

class UnderArmourSpider(scrapy.Spider):
    name = 'UnderArmourSpider'

    def __init__(self, shoe_arg, *args, **kwargs):
        super(UnderArmourSpider, self).__init__(*args, **kwargs)
        self.shoe_arg = shoe_arg

    def start_requests(self):
        url = f"https://www.underarmour.com/en-us/search/?q={self.shoe_arg}"
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
                # Get Gender
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

                # Check for sales price and get regular price as well
                item_sale_element = product.css('span.bfx-price.bfx-sale-price::text').get()
                regular_price = product.css('span.bfx-price.bfx-list-price::text').get().replace('$', '')
                if item_sale_element is not None:
                    sales_price = item_sale_element.replace('$', '')
                else:
                    # Use default price if no sale is present
                    sales_price = regular_price


                
                item['name'] = title
                item['link'] = "https://www.underarmour.com" + product.css('a.ProductTile_product-item-link__tSc19').attrib['href']
                item['image'] = product.css('img.Image_responsive_image__Hsr2N').attrib['src']
                item['original_price'] = regular_price
                item['sale_price'] = sales_price
                item['gender'] = gender
                item['vendor'] = 'UnderArmour'
                yield item
                
            except Exception as e:
                print(e)
                # item['name'] = 'No Data'
                # item['link'] = 'No Data'
                # item['image'] = 'No Data'
                # item['original_price'] = 'No Data'
                # item['sale_price'] = 'No Data'
                # item['gender'] = 'No Data'
                # yield item
                continue

        # next_page = response.css('a[aria-label="Go to the next page"]::attr(href)').get()
        # if next_page:
        #     next_page_url = 'https://www.underarmour.com' + next_page
        #     yield SeleniumRequest(
        #         url=next_page_url, 
        #         callback=self.parse,
        #         wait_time=5,
        #         wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.false.ProductTile_product-tile-container__flx2K.module__primary-img.false.ProductTile_split-view-enabled__eCRsC"))
        #     )
        # else:
        #     self.logger.info("No more pages found")

# process = CrawlerProcess(settings={
#     'SELENIUM_DRIVER_NAME': 'firefox',
#     'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],  # Optional: Headless mode
#     'SELENIUM_DRIVER_EXECUTABLE_PATH': 'geckodriver',
#     'DOWNLOADER_MIDDLEWARES': {
#         CustomSeleniumMiddleware: 800
#     },
#     'FEEDS': {
#         'results.json': {
#             'format': 'json',
#             'encoding': 'utf8',
#             'store_empty': False,
#             'indent': 4,
#             'overwrite': True,
#         },
#     },
#     'LOG_LEVEL': 'INFO',
# })

# process.crawl(UnderArmourSpider, 'charge assert')
# process.start()