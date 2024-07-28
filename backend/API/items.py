# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ShoeProduct(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    original_price = scrapy.Field()
    link = scrapy.Field()
    image = scrapy.Field()
    gender = scrapy.Field()
    sale_price = scrapy.Field()
    
