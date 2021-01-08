import json
import logging

from .items import Fashion, FashionItem
from scrapy.exporters import CsvItemExporter
from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)


class FashionPipeline:
    def open_spider(self, spider):
        self.items = open("../items.csv", "wb")
        self.fashion = open("../fashion.csv", "wb")
        
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
    
    
