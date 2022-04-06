# Crawler for SETI@home

## Requirements

- Python3
- Scrapy

## Config

To crawl the given users:

Change the `userids` iterable in `/SETI_Scrapy/spiders/SETI_spider.py`.

## Run the spider

```python
scrapy crawl SETI -O SETI.csv
```
