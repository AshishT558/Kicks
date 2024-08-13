import scrapy
from scrapy.crawler import CrawlerProcess
from items import ShoeProduct

class SkechersSpider(scrapy.Spider):
    name = 'SkechersSpider'

    def __init__(self, shoe_arg, *args, **kwargs):
        super(SkechersSpider, self).__init__(*args, **kwargs)
        self.shoe_arg = shoe_arg

    def start_requests(self):
        url = f"https://www.skechers.com/search/?q={self.shoe_arg}"
        yield scrapy.Request(url=url, callback=self.parse)

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
                item['vendor'] = 'Skechers'
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

        # next_page = response.css('a.btn.btn-redesign.btn-primary-ghost.btn-md.col-12.col-sm-4::attr(href)').get()
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)
        # else:
        #     self.logger.info("No more pages found")
        