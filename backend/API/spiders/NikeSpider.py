import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.crawler import CrawlerProcess
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from items import ShoeProduct
from custom_selenium_middleware import CustomSeleniumMiddleware

class NikeSpider(scrapy.Spider):
    name = "NikeSpider"

    def __init__(self, shoe_arg, *args, **kwargs):
        super(NikeSpider, self).__init__(*args, **kwargs)
        self.shoe_arg = shoe_arg

    def start_requests(self):
        url = f"https://www.nike.com/w?q={self.shoe_arg}"
        yield SeleniumRequest(url=url, 
                              callback=self.parse, 
                              wait_time=5,  # Increased wait time
                            wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-card")))

    def parse(self, response):
        for product in response.css('div.product-card'):
            
            gender_tag = product.css('div.product-card__subtitle::text').get()
            if "women's" in gender_tag.casefold():
                 gender = "Women"
            elif "men's" in gender_tag.casefold():
                gender = "Men"
            elif "kids'" in gender_tag.casefold():
                gender = "Kids"
            else:
                gender = "Unisex"

            # Check for sales price and get regular price as well
            item_sale_element = product.css('div.product-price.us__styling.is--striked-out.css-0::text').get()
            if item_sale_element is not None:
                sales_price = product.css('div.product-price.is--current-price.css-1ydfahe::text').get().replace('$', '')
                original_price = item_sale_element.replace('$', '')
            else:
                # Use default price if no sale is present
                original_price = product.css('div.product-price.us__styling.is--current-price.css-11s12ax::text').get().replace('$', '')  
                sales_price = original_price

            try:
                item = ShoeProduct()
                item['name'] = product.css('div.product-card__title::text').get()
                item['link'] = response.urljoin(product.css('a.product-card__link-overlay::attr(href)').get())
                item['image'] = product.css('img.product-card__hero-image.css-1fxh5tw::attr(src)').get()
                item['original_price'] = original_price
                item['sale_price'] = sales_price
                item['gender'] = gender
                item['vendor'] = 'Nike'
                yield item
            except Exception as e:
                # item['name'] = 'No Data'
                # item['link'] = 'No Data'
                # item['image'] = 'No Data'
                # item['original_price'] = 'No Data'
                # item['sale_price'] = 'No Data'
                # item['gender'] = 'No Data'
                # yield item
                continue
        # next_page = response.css('a.pagination-button.next::attr(href)').get()
        # if next_page:
        #     yield response.follow(next_page, self.parse)

# Setup the process and run the spider
# Setup the process and run the spider
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

# process.crawl(NikeSpider, 'air max 270')
# process.start()