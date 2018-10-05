#!/usr/bin/env python3
# coding=utf-8
# __author__: Alexander
import scrapy
from movie.items import DownloadItem
import pymysql
from movie import settings
from bs4 import BeautifulSoup
import datetime


class CiliMaoSpider(scrapy.spiders.Spider):
    name = "cilimao"
    start_urls = ['http://www.cilimao.me']
    allowed_domains = ['cilimao.me']
    item = DownloadItem()

    def parse(self, response):
        """
        根据t_movies表的download_url字段值的有无来整理要爬取的影片
        :param response: 响应到本地的文件
        :return:
        """
        search_url = "http://www.cilimao.me/search?word={}"
        connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)
        cursor = pymysql.cursors.SSCursor(connect)
        cursor.execute('select title,id,download_url from t_movies')

        while True:
            movie = cursor.fetchone()
            if movie is None:
                cursor.close()
                break
            if movie[2] is None:
                url = search_url.format(movie[0])

                yield scrapy.Request(url, callback=self.parse_main, meta={'id': movie[1]})

    def parse_main(self, response):
        """
        得到详细页面url
        """
        id = response.meta['id']
        soup = BeautifulSoup(response.body, 'lxml')
        second_url = self.start_urls[0]+soup.find('a', class_='MovieCard__title___2Xq-9').get('href')
        yield scrapy.Request(second_url, callback=self.parse_detail, meta={'id': id, 'cili_from': second_url})

    def parse_detail(self, response):
        """爬取字段"""
        soup = BeautifulSoup(response.body, 'lxml')
        li = soup.find('li', class_='MovieResources__ci_icon___1J-At')
        if li is not None:
            reactid = int(li.get('data-reactid'))
            cili_link = soup.find('a', attrs={'data-reactid': reactid+1}).get('href')
            size = soup.find('td', attrs={'data-reactid': reactid+4}).get_text()
            clear = soup.find('td', attrs={'data-reactid': reactid+5}).get_text()
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            cili_from = response.meta['cili_from']
            self.item['cili_from'] = cili_from
            self.item['createTime'] = date
            self.item['clear'] = clear
            self.item['size'] = size
            self.item['downloadUrl'] = cili_link
            self.item['movieId'] = response.meta['id']
            yield self.item
            # print('磁力来自{}'.format(cili_from))
            # print(date)
            # print('movieid{0}'.format(response.meta['id']))
            # print(cili_link)
            # print(size)
            # print(clear)





