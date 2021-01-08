# fashion crawler 

Fashion data(attributes, styling) crawler using Scrapy framework. 
[SSF shop](https://www.ssfshop.com) is now available

## Requirements
> - Python 3.6+
> - Chrome webdriver 

## Set up
```sh
pip install scrapy, selenium
```
```sh
cd fashion-crawler
scrapy crawl ssf -a keyword=[search keyword] -a page_count=[num of pages to read]
```