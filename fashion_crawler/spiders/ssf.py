import scrapy
import logging

import re
from scrapy import Request
# from scrapy_splash import SplashRequest

from fashion_crawler.items import Fashion, FashionItem

logger = logging.getLogger(__name__)

class SsfSpider(scrapy.Spider):
    name = 'ssf'
    allowed_domains = ['www.ssfshop.com']
    home_url = "https://www.ssfshop.com"
    search_url = "https://www.ssfshop.com/public/search/search/view?"

    def start_requests(self):
        try:
            self.page_count = int(self.page_count)
        except:
            self.page_count = self.settings.attributes['DEFAULT_PAGE_COUNT'].value
            logger.info(f'Page count is set to default value {self.page_count}')
        
        # get item id info
        for page in range(1, self.page_count+1):
            logger.info(f'Parse page {page} with keyword={self.keyword}')
            
            yield Request(\
                    url=f"{self.search_url}keyword={self.keyword}&pageNo={page}&orderView=SORT_SALE_IDEX", \
                    callback=self.parse_item_url)
    
    # get all urls of item page in item list
    def parse_item_url(self, response):
        for url in response.xpath('//div[@class="list_goods "]/ul/li/a/@href').getall():
            yield Request(\
                    url=f"{self.home_url}{url}", \
                    callback=self.parse_fashion)

    # get all ids of items in item list
    def parse_ids(self, response):
        for gid in response.xpath('//div[@class="list_goods "]/ul/li/@view-godno').getall():
            logger.info(f'Start parsing item id : {gid}')
            yield Request(\
                    url=f"{self.search_url}keyword={gid}", \
                    callback=self.parse_item)
    
    # get matched fashion items and get all attributes of the items
    def parse_fashion(self, response):
        # weared fashion
        list_goods = response.xpath('//div[@class="styled_with"]/div[@class="list_goods"]')
        current_item_id = response.request.url.split('/')[4]
        
        if list_goods:
            fashion = Fashion()
            fashion['item_ids'] = [current_item_id]
            fashion['item_ids'] += [gid.get() for gid in list_goods.xpath('ul/li/@view-godno')]

            yield fashion 
            
            for goods_id in fashion['item_ids']:
                logger.info(f'Start parsing wearing item (id : {goods_id})')
                yield Request(\
                        url=f"{self.search_url}keyword={goods_id}", \
                        callback=self.parse_item)

        # ssf recommend fashion
        list_goods = response.xpath('//div[@class="styling"]/div[@class="list_goods"]')
        if list_goods:
            fashion = Fashion()
            fashion['item_ids'] = [current_item_id]
            
            id_from_imgsrc = lambda x: x.split('/')[-1].split('_')[0]
            
            fashion['item_ids'] += [
                id_from_imgsrc(imgsrc.get()) 
                for imgsrc 
                in list_goods.xpath('//ul[2]/li/a/img/@src')]
            
            yield fashion
        
            for goods_id in fashion['item_ids']:
                logger.info(f'Start parsing recommended item (id : {goods_id})')
                yield Request(\
                        url=f"{self.search_url}keyword={goods_id}", \
                        callback=self.parse_item)
    
    # parse attributes in filter
    def parse_item(self, response):
        item = FashionItem()
        item['id'] = response.xpath('//*[@id="searchForm"]/input[2]/@value').get()
        
        goods = response.xpath('//*[@id="searchGoodsList"]/ul/li/a')
        item['name'] = goods.xpath('div[@class="info"]/span[2]/text()').get().strip()
        
        # get hover image first
        item['img_url'] = goods.xpath('span/img/@src').get() 
        if not item['img_url']:
            item['img_url'] = goods.xpath('img/@src').get()
        
        item['brand'] = '/'.join(\
            response.xpath('//*[@id="sorting_filter"]/ul/li/label/text()').getall())
        
        # select smartfilter
        smartfilter = response.xpath('//*[@id="smartFilter"]')
        for tab in smartfilter.xpath('//div[@class="tabs"]/div[contains(@id,"tab")]'):
            container = tab.xpath('div[1]/div[1]')
            attr_name = container.xpath('h3/text()').get()
            
            # get attributes by name
            if attr_name == '카테고리':
                for li in container.xpath('ul/li'):
                    big_category = li.xpath('descendant::*/text()[not(parent::*[@class="wa_hidden"])]')
                    
                    if not item.get('category'):
                        item['category'] = []
                    item['category'].append(\
                        '>'.join(''.join(big_category.getall()).split()))
            
            if attr_name == '종류':
                item['category_detail'] = container.xpath('ul/li/div/ul/li/label/text()').get()
                    
            elif attr_name == '색상/패턴':
                item['color'] = container.xpath('ul/li/span/label/text()').get()
                pattern = container.xpath('ul/li/label/text()').getall()
                if pattern:
                    pattern = ''.join(pattern).split()
                    item['pattern'] = pattern
            
            elif attr_name == '소재':
                item['materials'] = container.xpath('ul[contains(@class,"check_list")]/li/label/text()').getall()
            
            elif attr_name == 'Style':
                item['style'] = container.xpath('ul[contains(@class,"check_list")]/li/label/text()').getall()
            
            elif attr_name == 'TPO':
                item['tpo'] = container.xpath('ul/li/label/text()').getall()
            
            elif attr_name == '길이':
                item['length'] = container.xpath('ul/li/div/ul/li/label/text()').getall()

        
        logger.info(f'Complete parsing attributes (id : {item["id"]})')
        
        yield item
                
            
            
        

        
        