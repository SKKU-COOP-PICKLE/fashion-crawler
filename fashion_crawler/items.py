# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Fashion(scrapy.Item):
    item_ids = scrapy.Field()

class FashionItem(scrapy.Item):
    id = scrapy.Field()
    brand = scrapy.Field()
    name = scrapy.Field()
    img_url = scrapy.Field()
    category = scrapy.Field()
    category_detail = scrapy.Field()
    color = scrapy.Field()
    tpo = scrapy.Field()
    pattern = scrapy.Field()
    style = scrapy.Field()
    materials = scrapy.Field()
    fit = scrapy.Field()
    length = scrapy.Field()
