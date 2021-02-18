# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes

from scrapy.settings import Settings

class FashionSeleniumSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class FashionSeleniumDownloaderMiddleware:
    
    def __init__(self, chrome_path, wait_time):
        self.chrome_path = chrome_path
        self.wait_time = wait_time
    
    @classmethod
    def from_crawler(cls, crawler):
        chrome_path = crawler.settings.get('CHROME_DRIVER_PATH')
        wait_time = crawler.settings.get('WEBDRIVER_WAIT_TIME')
        
        ext = cls(chrome_path, wait_time)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext
    
    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless") # run without an actual browser window.
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=self.chrome_path, chrome_options=chrome_options)
        driver.implicitly_wait(self.wait_time)
        self.driver = driver
        
    def spider_closed(self, spider):
        self.driver.quit()

    def process_request(self, request, spider):
        self.driver.get(request.url)
        
        body = to_bytes(text=self.driver.page_source)
        return HtmlResponse(url=request.url, body=body, encoding='utf-8', request=request)

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass