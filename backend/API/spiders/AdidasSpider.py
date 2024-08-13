import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from custom_selenium_middleware import CustomSeleniumMiddleware
from items import ShoeProduct

class AdidasSpider(scrapy.Spider):
    name = 'AdidasSpider'

    def __init__(self, shoe_arg, *args, **kwargs):
        super(AdidasSpider, self).__init__(*args, **kwargs)
        self.shoe_arg = shoe_arg

    def start_requests(self):
        url = f"https://www.adidas.com/us/search?q={self.shoe_arg}"
        yield SeleniumRequest(
                url=url, 
                callback=self.parse,
                wait_time=5,  # Increased wait time
                wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.gl-price.gl-price--horizontal.notranslate.gl-price--inline___3nMlh"))
            )
# gl-price-item.notranslate
# gl-price gl-price--horizontal notranslate gl-price--inline___3nMlh
    def parse(self, response):
        
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
                    sales_price = item_sale_element.replace('$', '')
                    original_price = product.css('div.gl-price-item.gl-price-item--crossed.notranslate::text').get().replace('$', '')
                else:
                    # Use default price if no sale is present
                    original_price = product.css('div.gl-price-item.notranslate::text').get().replace('$', '')
                    sales_price = original_price
                
                #because some prices show as null
                if original_price is None or sales_price is None:
                    continue

                item['name'] = product.css('p.glass-product-card__title::text').get()
                item['link'] = "https://www.adidas.com/" + product.css('a.glass-product-card__assets-link').attrib['href']
                item['image'] = product.css('img.product-card-image.glass-product-card__image.glass-product-card__primary-image').attrib['src']
                item['original_price'] = original_price
                item['sale_price'] = sales_price
                item['gender'] = gender
                item['vendor'] = 'Adidas'
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