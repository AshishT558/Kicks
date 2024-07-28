import scrapy
from scrapy.crawler import CrawlerProcess
from items import ShoeProduct

class SkechersSpider(scrapy.Spider):
    name = 'SkechersSpider'
    shoe_name = "cali breeze"
    start_urls = [f"https://www.skechers.com/search/?q={shoe_name}"]

    def parse(self, response):
        #Commented out Debugging
        # self.logger.info(f"Visited {response.url}")

        # # Print the HTML content for debugging
        # with open('page_source.html', 'w') as f:
        #     f.write(response.text)

        product_selector = "div.product"
        products = response.css(product_selector)
        
        #Commented out Debugging
        # self.logger.info(f"Found {len(products)} products")

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

                # # Check for sales price vs price range vs single price
                # item_sale_element = product.css('span.bfx-price.bfx-sale-price::text').get()
                # regular_price = product.css('span.bfx-price.bfx-list-price::text').get().replace('$', '')
                # if item_sale_element is not None:
                #     sales_price = item_sale_element.replace('$', '')
                # else:
                #     # Use default price if no sale is present
                #     sales_price = regular_price


                # Check for sales price vs price range vs single price
                
                # Check count of 'span.value' - IF there is only one there is no sale or price range
                span_values = product.css('span.value::attr(content)')

                # Check count of 'span.sales' - IF there is only one there is a sale, IF there is two there is a range
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
                yield item
                
            except Exception as e:
                #Commented out Debugging
                # self.logger.error(f"Error parsing product: {e}")
                item['name'] = 'No Data'
                item['link'] = 'No Data'
                item['image'] = 'No Data'
                item['original_price'] = 'No Data'
                item['sale_price'] = 'No Data'
                item['gender'] = 'No Data'
                yield item

        next_page = response.css('a.btn.btn-redesign.btn-primary-ghost.btn-md.col-12.col-sm-4::attr(href)').get()
        if next_page is not None:
            #Commented out Debugging
            # self.logger.info(f"Next page: {next_page_url}")
            return response.follow(next_page, callback=self.parse)
        else:
            self.logger.info("No more pages found")
        
