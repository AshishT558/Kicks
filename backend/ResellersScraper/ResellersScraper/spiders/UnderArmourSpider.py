import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class UnderArmourSpider(scrapy.Spider):
    name = 'UnderArmourSpider'
    shoe_name = "slipspeed"
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
        #Commented out Debugging
        # self.logger.info(f"Visited {response.url}")

        # # Print the HTML content for debugging
        # with open('page_source.html', 'w') as f:
        #     f.write(response.text)

        product_selector = "div.false.ProductTile_product-tile-container__flx2K.module__primary-img.false.ProductTile_split-view-enabled__eCRsC"
        products = response.css(product_selector)
        
        #Commented out Debugging
        # self.logger.info(f"Found {len(products)} products")

        for product in products:
            try:
                # Get Gender
                title = product.css('a.ProductTile_product-item-link__tSc19::text').get()
                if "men's" in title.casefold():
                    gender = "Men"
                elif "women's" in title.casefold():
                    gender = "Women"
                elif "unisex" in title.casefold():
                    gender = "Unisex"
                else:
                    gender = "Unknown"

                # # Check for sales price
                # item_sale_element = product.css('span.bfx-price.bfx-sale-price::text')
                # if item_sale_element:
                #     price = item_sale_element.replace('$', '')
                # else:
                #     #use default price if no sale is present
                #     price = product.css('span.bfx-price.bfx-list-price::text').get().replace('$', '')

                yield {
                    'Name': title,
                    'Price': product.css('span.bfx-price.bfx-list-price::text').get().replace('$', ''),
                    'Link': product.css('a.ProductTile_product-item-link__tSc19').attrib['href'],
                    'Image': product.css('img.Image_responsive_image__Hsr2N').attrib['src'],
                    'Gender': gender
                }
            except Exception as e:
                #Commented out Debugging
                # self.logger.error(f"Error parsing product: {e}")
                yield {
                    'Name': 'No data',
                    'Price': 'No data',
                    'Link': 'No data',
                    'Image': 'No data',
                    'Gender': 'No data'
                }

        next_page = response.css('a[aria-label="Go to the next page"]::attr(href)').get()
        if next_page:
            next_page_url = 'https://www.underarmour.com' + next_page
            #Commented out Debugging
            # self.logger.info(f"Next page: {next_page_url}")
            yield SeleniumRequest(
                url=next_page_url, 
                callback=self.parse,
                wait_time=5,
                wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.false.ProductTile_product-tile-container__flx2K.module__primary-img.false.ProductTile_split-view-enabled__eCRsC"))
            )
        else:
            self.logger.info("No more pages found")

# Setup the process and run the spider
process = CrawlerProcess(settings={
    'SELENIUM_DRIVER_NAME': 'chrome',
    'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],  # Optional: Headless mode
    'SELENIUM_DRIVER_EXECUTABLE_PATH': '/Users/adic/Desktop/CODE/Kicks/backend/ResellersScraper/ResellersScraper/spiders/chromedriver',
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy_selenium.SeleniumMiddleware': 800
    },
    'FEEDS': {
        'backend/ResellersScraper/results.json': {
            'format': 'json',
            'encoding': 'utf8',
            'store_empty': False,
            'indent': 4,
        },
    },
    'LOG_LEVEL': 'INFO',
})

process.crawl(UnderArmourSpider)
process.start()
