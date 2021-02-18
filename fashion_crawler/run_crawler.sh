#!/bin/bash


# for keyword in "코트" "재킷" "점퍼" "패딩" "로브" "가디건" "집업" "베스트" "티셔츠" "블라우스" "셔츠" "니트" "후드티" "맨투맨" "카라티" "팬츠" "슬랙스" "청바지" "원피스" "오버롤"
#     do
#         echo "Start Crawling $keyword"
#         scrapy crawl ssf -a keyword="$keyword" -a start_page=1 -a end_page=15& \
#     done

for keyword in "코트" "재킷" "점퍼" "패딩" "가디건" "티셔츠" "블라우스" "셔츠" "니트" "후드티" "맨투맨" "팬츠" "슬랙스" "청바지" "원피스"
    do
        echo "Start Crawling $keyword"
        scrapy crawl ssf -a keyword="$keyword" -a start_page=26 -a end_page=40& \
    done
