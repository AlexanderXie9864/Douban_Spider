# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    """豆瓣爬虫items"""
    title = scrapy.Field()
    year = scrapy.Field()
    country = scrapy.Field()
    lan = scrapy.Field()
    douban_link = scrapy.Field()
    introduce = scrapy.Field()
    main_actor = scrapy.Field()
    img_url = scrapy.Field()
    length = scrapy.Field()
    director = scrapy.Field()
    local_img_url = scrapy.Field()

    image_urls = scrapy.Field()


class DownloadItem(scrapy.Item):
    """获取磁力信息的items"""
    movieId = scrapy.Field()
    downloadUrl = scrapy.Field()
    size = scrapy.Field()
    clear = scrapy.Field()
    createTime = scrapy.Field()
    cili_from =scrapy.Field()

    pass



