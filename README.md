# fashion crawler 

Fashion data(attributes, styling) crawler using Scrapy framework. 
[SSF shop](https://www.ssfshop.com) is now available

## Requirements
> - Python 3.6+
> - Chrome webdriver 

## Set up
```sh
pip install scrapy selenium
```

## Usage
### Inserting to Database
Modify `ITEM_PIPELINES` and `DB_SETTINGS` in `settings.py`, `FashionDatabasePipeline` in `pipelines.py`


### Crawl by keyword
```sh
cd fashion-crawler
scrapy crawl ssf -a keyword=[search keyword] -a start_page=[first page to crawl] -a end_page=[last page to crawl]
```

### Crawl by page url
```sh
cd fashion-crawler
scrapy crawl ssf -a page_url=[page_url] -a start_page=[first page to crawl] -a end_page=[last page to crawl]
```
