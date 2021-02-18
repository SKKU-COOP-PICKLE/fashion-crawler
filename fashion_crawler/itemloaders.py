import re
import typing
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, Join, Compose, TakeFirst


# remove blank space, None in list and string
def normalize(item):
    if isinstance(item, list):
        item = [normalize(x) for x in item if x]
        return [x for x in item if x]
    
    if isinstance(item, str):
        return re.sub(r"\s+", " ", item).strip()
    
    return item

# def remove_words(item):
#     WORDS_TO_REMOVED = ('전체', 'Home')
#     return [[x for x in item if x not in WORDS_TO_REMOVED]]

# def categorize(items):
#     if len(items) > 1:
#         result = []
#         for item in zip(*items):
#             item = set(item)
#             if 'WOMEN' in item and 'MEN' in item:
#                 item = 'UNISEX'
#             else:
#                 item = ','.join(item)
#             result.append(item)
#         return result
            
#     else:
#         return sum(items, [])

class FashionItemLoader(ItemLoader):
    default_input_processor = Compose(normalize)
    length_in = Compose(set, list, sorted)
    
    brand_out = Join('/')
    price_out = Compose(lambda x: x[0].replace(',',''))
    wish_out = Compose(TakeFirst(),int)
    category_out = Compose(Join('>'))
    default_output_processor = Compose(set,list, sorted, Join(','))
    

class FashionLoader(ItemLoader):
    item_ids_in = Compose(set, list) # remove duplicated items
    item_ids_out = Compose(sorted)