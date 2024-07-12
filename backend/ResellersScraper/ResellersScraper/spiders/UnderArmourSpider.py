import scrapy
from scrapy.crawler import CrawlerProcess

class UnderArmourSpider(scrapy.Spider):
    name = 'UnderArmourSpider'
    start_urls = ["https://www.underarmour.com/en-us/c/shoes/"]

    def parse(self, response):
        for products in response.css("div.false.ProductTile_product-tile-container__flx2K.module__primary-img.false.ProductTile_split-view-enabled__eCRsC"):
            try:
                title = products.css('a.ProductTile_product-item-link__tSc19::text').get()
                if "men's" in title.casefold():
                    gender = "Men"
                elif "women's" in title.casefold():
                    gender = "Women"
                elif "unisex" in title.casefold():
                    gender = "Unisex"
                else:
                    gender = "Unknown"

                yield {
                    'Name': products.css('a.ProductTile_product-item-link__tSc19::text').get(),
                    'Price': products.css('span.bfx-price.bfx-list-price::text').get().replace('$', ''),
                    'Link': products.css('a.ProductTile_product-item-link__tSc19').attrib['href'],
                    'Image': products.css('img.Image_responsive_image__Hsr2N').attrib['src'],
                    'Gender': gender
                }
            except:
                yield {
                    'Name': 'No data',
                    'Price': 'No data',
                    'Link': 'No data',
                    'Image': 'No data',
                }
        
        next_page = response.css('a[aria-label = "Go to the next page"]').attrib['href']
        if next_page:
            next_page_url = 'https://www.underarmour.com' + next_page
            print(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

# Setup the process and run the spider
process = CrawlerProcess(settings={
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