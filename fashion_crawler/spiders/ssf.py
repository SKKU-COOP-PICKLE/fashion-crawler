import os
import re
import logging

import scrapy
from scrapy import Request
from itemloaders.processors import TakeFirst
# from scrapy_splash import SplashRequest

from fashion_crawler.items import Fashion, FashionItem
from fashion_crawler.itemloaders import FashionItemLoader, FashionLoader

logger = logging.getLogger(__name__)

class SsfSpider(scrapy.Spider):
    name = 'ssf'
    home_url = "https://www.ssfshop.com"
    search_url = "https://www.ssfshop.com/public/search/search/view?"
    keyword = None
    page_url = None

    def start_requests(self):
        self.start_page = int(self.start_page)
        self.end_page = int(self.end_page)
        logger.info(f'Start crawling pages from {self.start_page} to {self.end_page}')
            
        
        # get item id info
        for page in range(self.start_page, self.end_page+1):
            if self.keyword:
                logger.info(f'Parse page {page} with keyword={self.keyword}')
                logger.info(f'Request URL: {f"{self.search_url}keyword={self.keyword}&pageNo={page}"}')
                yield Request(url=f"{self.search_url}keyword={self.keyword}&pageNo={page}", callback=self.parse_item_url)
            elif self.page_url:
                logger.info(f'Parse page {self.page_url}')
                logger.info(f'Request URL: {f"{self.page_url}&currentPage={page}"}')
                yield Request(url=f"{self.page_url}&currentPage={page}", callback=self.parse_item_url)
    
    # get all urls of item page in item list
    def parse_item_url(self, response):
        for url in response.xpath('//div[contains(@class, "list_goods")]/ul/li/a/@href').getall():
            if url.startswith('javascript:goToProductDetail'):
                brand, item_id = url.split("'")[1], url.split("'")[3]
                url = f'https://www.ssfshop.com/{brand}/{item_id}/good?$set:1$$dpos:2'
                yield Request(url=url, callback=self.parse_fashion)
            else:
                yield Request(url=f"{self.home_url}{url}", callback=self.parse_fashion)

    # get all ids of items in item list
    def parse_ids(self, response):
        for gid in response.xpath('//div[contains(@class, "list_goods")]/ul/li/@view-godno').getall():
            # logger.info(f'Start parsing item id : {gid}')
            yield Request(url=f"{self.search_url}keyword={gid}", callback=self.parse_item)
    
    # get matched fashion items and get all attributes of the items
    def parse_fashion(self, response):
        category = [x.strip() for x in response.xpath('//*[@id="location"]/span/a/text()').getall() if x]
        if 'LIFE' in category or 'KIDS' in category:
            return
        
        # weared fashion
        list_goods = {
            'wearing' : response.xpath('//div[@class="styled_with"]/div[@class="list_goods"]'),
            'recommendation' : response.xpath('//div[@class="styling"]/div[@class="list_goods"]')
        }
        
        for fashion_type, list_good in list_goods.items():
            current_item_id = response.request.url.split('/')[4]
            if list_good:
                loader = FashionLoader(item=Fashion(), response=response)
                loader.add_value('id', f"{str.upper(fashion_type[0])+current_item_id}")
                loader.add_value('site', self.name)
                loader.add_value('type', fashion_type)
                loader.add_value('item_ids', [current_item_id])
                
                if fashion_type == 'wearing':
                    loader.add_value('item_ids', [gid.get() for gid in list_good.xpath('ul/li/@view-godno')])
                    yield loader.load_item()
                else:
                    id_from_src = lambda x: x.split('/')[-1].split('_')[0]
                    loader.add_value('item_ids', [id_from_src(src.get()) for src in list_good.xpath('//ul[2]/li/a/img/@src')])
                    yield loader.load_item() 
                
                for goods_id in loader.get_output_value('item_ids'):
                    # logger.info(f'Start parsing {fashion_type} item (id : {goods_id})')
                    yield Request(url=f"{self.search_url}keyword={goods_id}", callback=self.parse_attributes_in_filter, dont_filter=True)
                    
    # 상세페이지에서 category만 parsing
    def parse_category(self, response):
        loader = FashionItemLoader(item=response.meta['item'], response=response)
        category = [x.strip() for x in response.xpath('//*[@id="location"]/span/descendant::text()').getall() if x]
        category = [x for x in category if x and x != 'Home' and x != 'OUTLET']
        if len(category) > 0:
            if (category[0] == 'WOMEN' or category[0] == 'MEN') and not loader.get_output_value('sex'):
                loader.add_value('sex', category[0])
            loader.add_value('category', category[1:])
        loader.add_xpath('wish', '//*[@id="wishLabel"]/text()')
        
        yield loader.load_item()
    
    # parse attributes in filter
    def parse_attributes_in_filter(self, response):
        loader = FashionItemLoader(item=FashionItem(), response=response)
        
        loader.add_xpath('id', '//*[@id="searchForm"]/input[2]/@value')
        
        goods_loader = loader.nested_xpath('//*[@id="searchGoodsList"]/ul/li/a')
        goods_loader.add_xpath('name','div[@class="info"]/span[@class="name"]/text()')
        goods_loader.add_xpath('price', 'div[@class="info"]/span[@class="price"]/text()')
        goods_loader.add_xpath('img_url','img/@src')
        detail_url = goods_loader.get_xpath('@href', TakeFirst())
        if not detail_url:
            return
        
        goods_loader.add_value('detail_url', f"{self.home_url}{detail_url}")
        
        # select smartfilter
        for selector in response.xpath('//div[starts-with(@id, "mCSB") and contains(@id,"container")]'):
            loader.selector = selector
            
            attr_name = loader.get_xpath('h3/text()', TakeFirst())
            
            # get attributes by name
            if attr_name == '브랜드':
                loader.add_xpath('brand','div/ul/li/label/text()')

            elif attr_name == '카테고리':
                if len(selector.xpath('.//ul/li[contains(@id, "li_a")]')) >= 2:
                    loader.add_value('sex', 'UNISEX')
            
            elif attr_name == '종류':
                loader.add_xpath('kind', 'ul/li/div/ul/li/label/text()')
                    
            elif attr_name == '색상/패턴':
                loader.add_xpath('color', 'ul[1]/li/span/label/text()')
                loader.add_xpath('pattern', 'ul[2]/li/label/text()')
            
            elif attr_name == '소재':
                loader.add_xpath('materials', 'ul/li/label/text()')
            
            elif attr_name == '핏':
                loader.add_xpath('fit', 'ul/li/div/ul/li/label/text()')
            
            elif attr_name == 'Style':
                loader.add_xpath('style', 'ul/li/label/text()')
            
            elif attr_name == 'TPO':
                loader.add_xpath('tpo', 'ul/li/label/text()')
            
            elif attr_name == '길이':
                loader.add_xpath('length', 'ul/li/div/ul/li/label/text()')
        
        item = loader.load_item()
        yield Request(url=f"{item.get('detail_url')}", callback=self.parse_category, meta={'item': item}, dont_filter=True)