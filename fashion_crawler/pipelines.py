import json
import logging

# database
import pymysql
from scrapy.exceptions import NotConfigured

from fashion_crawler.items import Fashion, FashionItem
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter

from datetime import datetime

logger = logging.getLogger(__name__)

class FashionCSVPipeline:
    def open_spider(self, spider):
        date = datetime.now().strftime('%Y_%m_%d')
        self.items = open(f"../items_{date}.csv", "ab")
        self.fashion = open(f"../fashion_{date}.csv", "ab")
        
        self.item_exporter = CsvItemExporter(self.items, encoding='utf8')
        self.fashion_exporter = CsvItemExporter(self.fashion, encoding='utf8')
        
        logger.info(f'Start exporting')
        self.item_exporter.start_exporting()
        self.fashion_exporter.start_exporting()
    
    def close_spider(self, spider):
        logger.info(f'Exporting is finished')
        self.item_exporter.finish_exporting()
        self.fashion_exporter.finish_exporting()
        self.items.close()
        self.fashion.close()
        
    def process_item(self, item, spider):
        if isinstance(item, Fashion):
            return self.handle_fashion(item, spider)
        if isinstance(item, FashionItem):
            return self.handle_fashion_item(item, spider)
    
    def handle_fashion_item(self, item, spider):
        self.item_exporter.export_item(item)
        return item
    
    def handle_fashion(self, item, spider):
        self.fashion_exporter.export_item(item)
        return item


class FashionDatabasePipeline:
    def __init__(self, user, host, passwd, port, db):
        self.user = user
        self.host = host
        self.passwd = passwd
        self.port = port
        self.db = db
        
    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise NotConfigured
        
        return cls(**db_settings)
        
    def open_spider(self, spider):
        self.conn = pymysql.connect(
                                db=self.db,
                                user=self.user,
                                passwd=self.passwd,
                                host=self.host,
                                port=self.port,
                                charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()
    
    def close_spider(self, spider):
        self.conn.close()
    
    def process_item(self, item, spider):
        if isinstance(item, Fashion):
            return self.handle_fashion_match(item, spider)
        if isinstance(item, FashionItem):
            return self.handle_fashionitem(item, spider)
    
    def handle_fashionitem(self, item, spider):
        field_names = [
            'id','brand','img_url',
            'detail_url','name','sex','old_category',
            'kind','color','tpo','pattern','style',
            'materials','fit','length',
            'price','wish']
        try:
            sql = "INSERT IGNORE INTO `items` " + "("+", ".join(field_names)+")" + \
                " VALUES " + "(" + ", ".join(["%s"]*len(field_names)) + ")"
                
            self.cursor.execute(sql,tuple([item.get(field) if field != 'old_category' else item.get('category') for field in field_names]))
            self.conn.commit()
            
        except pymysql.err.IntegrityError as e:
            logger.error(e)
        
        return item
    
    def handle_fashion_match(self, item, spider):
        sql = "INSERT IGNORE INTO `fashions` (`id`, `site`, `type`) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (item.get("id"), item.get("site"), item.get("type")))

        sql = "INSERT IGNORE INTO `fashion_to_item` (fashion_id, item_id) VALUES (%s, %s)"
        for item_id in item.get("item_ids"):
            self.cursor.execute(sql,(item.get("id"), item_id))
        self.conn.commit()
        return item
    