import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from custom_selenium_middleware import CustomSeleniumMiddleware
from items import ShoeProduct

class AdidasSpider(scrapy.Spider):
    name = 'AdidasSpider'
    shoe_name = "NMD"
    start_urls = [f"https://www.adidas.com/us/search?q={shoe_name}"]

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url, 
                callback=self.parse,
                wait_time=10,  # Increased wait time
                wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.gl-price-item.notranslate"))
            )

    def parse(self, response):
        # Capture screenshot for debugging
        driver = response.meta['driver']
        driver.save_screenshot('screenshot.png')

        product_selector = "div.grid-item"
        products = response.css(product_selector)
        
        for product in products:
            item = ShoeProduct()
            try:
                # Get Gender
                gender_tag = product.css('p.glass-product-card__category::text').get()
                if "women's" in gender_tag.casefold():
                    gender = "Women"
                elif "men's" in gender_tag.casefold():
                    gender = "Men"
                elif "boy's" in gender_tag.casefold():
                    gender = "Kids"
                elif "girl's" in gender_tag.casefold():
                    gender = "Kids"
                else:
                    gender = "Unisex"

                # Check for sales price and get regular price as well
                item_sale_element = product.css('div.gl-price-item.gl-price-item--sale.notranslate::text').get()
                if item_sale_element is not None:
                    sales_price = item_sale_element
                    original_price = product.css('div.gl-price-item.gl-price-item--crossed.notranslate::text').get()
                else:
                    # Use default price if no sale is present
                    original_price = product.css('div.gl-price-item.notranslate::text').get()
                    sales_price = original_price
                
                item['name'] = product.css('p.glass-product-card__title::text').get()
                item['link'] = product.css('a.glass-product-card__assets-link').attrib['href']
                item['image'] = product.css('img.product-card-image.glass-product-card__image.glass-product-card__primary-image').attrib['src']
                item['original_price'] = original_price
                item['sale_price'] = sales_price
                item['gender'] = gender
                yield item
                
            except Exception as e:
                item['name'] = 'No Data'
                item['link'] = 'No Data'
                item['image'] = 'No Data'
                item['original_price'] = 'No Data'
                item['sale_price'] = 'No Data'
                item['gender'] = 'No Data'
                yield item

        # next_page = response.css('a.active.gl-cta.gl-cta--tertiary::attr(href)').get()
        # if next_page:
        #     next_page_url = 'https://www.Adidas.com' + next_page
        #     yield SeleniumRequest(
        #         url=next_page_url, 
        #         callback=self.parse,
        #         wait_time=10,  # Increased wait time
        #         wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.glass-product-card-container.with-variation-carousel"))
        #     )
        # else:
        #     self.logger.info("No more pages found")
        
# Setup the process and run the spider
process = CrawlerProcess(settings={
    'SELENIUM_DRIVER_NAME': 'firefox',
    'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],  # Optional: Headless mode
    'SELENIUM_DRIVER_EXECUTABLE_PATH': '/Users/adic/Desktop/CODE/Kicks/backend/ResellersScraper/ResellersScraper/spiders/geckodriver',
    'DOWNLOADER_MIDDLEWARES': {
        CustomSeleniumMiddleware: 800
    },
    'FEEDS': {
        'backend/ResellersScraper/Adidas-results.json': {
            'format': 'json',
            'encoding': 'utf8',
            'store_empty': False,
            'indent': 4,
            'overwrite': True,
        },
    },
    'LOG_LEVEL': 'INFO',
})

process.crawl(AdidasSpider)
process.start()
