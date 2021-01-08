import scrapy
import logging

from scrapy import Request
# from scrapy_splash import SplashRequest

from ..items import FashionItem

logger = logging.getLogger(__name__)

class LfSpider(scrapy.Spider):
    name = 'lf'
    allowed_domains = ['lfmall.co.kr']
    start_urls = ['http://lfmall.co.kr/']

    def parse(self, response):
        pass
