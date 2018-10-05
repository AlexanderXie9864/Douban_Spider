#!/usr/bin/env python3
# coding=utf-8
# __author__: Alexander
import scrapy
from movie.items import MovieItem
import json
from bs4 import BeautifulSoup


class DoubanSpider(scrapy.spiders.Spider):
    name = "douban"
    start_urls = ['https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%94%B5%E5%BD%B1']
    allowed_domains = ['movie.douban.com']
    item = MovieItem()

    def parse(self, response):
        """爬虫入口"""
        start = int(input('起始地址：'))
        num = int(input('爬取数量(20的倍数)：'))
        step = 20

        for count in range(start, start+num, step):
            json_url = 'https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=&start={}'.format(count)
            yield scrapy.Request(
                json_url,
                callback=self.parse_main,
            )

    def parse_main(self, response):
        """获取json文件内有用内容"""
        info = json.loads(response.body.decode('utf-8'))
        data_dic = info['data']
        for data in data_dic:
            movie_id = str(data['id'])
            if data['url']:

                yield scrapy.Request(data['url'], callback=self.parse_detail, meta={'id': movie_id,
                                                                                    'title': data['title'],
                                                                                    'cover': data['cover'],
                                                                                    })

    def parse_detail(self, response):
        movie_id = response.meta['id']
        douban_link = 'http://movie.douban.com/subject/{}/'.format(movie_id)
        self.item['douban_link'] = douban_link
        self.item['title'] = response.meta['title']
        self.item['img_url'] = response.meta['cover']

        self.item['image_urls'] = [response.meta['cover']]  # scrapy框架特有的图片下载必要字段
        soup = BeautifulSoup(response.body, 'lxml')

        director = soup.find_all('span', class_='attrs')[0].get_text()
        main_actor = soup.find_all('a', attrs={'rel': "v:starring"})[0].get_text()
        length = soup.find('span', attrs={'property': "v:runtime"}).get_text()
        year = soup.find('span', attrs={'property': "v:initialReleaseDate"}).get_text().split('-')[0]

        # 爬取国家、语言，检查爬取内容是否是中文字段，如果不是则认定为其他东西，并修改爬取标签属性
        check_item = response.xpath('//*[@id="info"]').re(r'</span> (.*)<br>\n')[1]
        result = self.check_contain_chinese(check_item)
        if result:
            country = response.xpath('//*[@id="info"]').re(r'</span> (.*)<br>\n')[1]
            lan = response.xpath('//*[@id="info"]').re(r'</span> (.*)<br>\n')[2]
        else:
            country = response.xpath('//*[@id="info"]').re(r'</span> (.*)<br>\n')[2]
            lan = response.xpath('//*[@id="info"]').re(r'</span> (.*)<br>\n')[3]
        # 简介(先隐藏后不隐藏的)
        try:
            introduce = soup.find('span', class_='all hidden').get_text()
        except:
            introduce = soup.find('span', attrs={'property': 'v:summary'}).get_text()
        self.item['director'] = director
        self.item['main_actor'] = main_actor
        self.item['length'] = length
        self.item['country'] = country
        self.item['lan'] = lan
        self.item['introduce'] = introduce.replace(' ', '')
        self.item['year'] = year
        yield self.item

    def check_contain_chinese(self, check_str):
        """检查是否包含中文字段"""
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False


