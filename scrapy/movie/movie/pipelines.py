# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import pymysql
import scrapy
import shutil
from movie import settings
from scrapy.pipelines.images import ImagesPipeline
from movie import items


class DBPipeline:
    """数据库存储管道"""

    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        """处理，判断item实例后进行相应操作"""
        if isinstance(item, items.MovieItem):
            try:
                self.cursor.execute(
                    """select * from t_movies where douban_link = %s""",
                    item['douban_link'])
                # 是否有重复数据
                repetition = self.cursor.fetchone()
                # 重复
                if repetition:
                    pass
                # 插入数据
                else:
                    self.cursor.execute("""
                                        insert into t_movies(title, 
                                                                    year, 
                                                                    country, 
                                                                    lan, 
                                                                    douban_link, 
                                                                    introduce,
                                                                    main_actor,
                                                                    img_url,
                                                                    length,
                                                                    director,
                                                                    local_img_url )
                                        value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                        (item['title'],
                                         item['year'],
                                         item['country'],
                                         item['lan'],
                                         item['douban_link'],
                                         item['introduce'],
                                         item['main_actor'],
                                         item['img_url'],
                                         item['length'],
                                         item['director'],
                                         item['local_img_url']
                                         ))
                # 提交sql语句
                self.connect.commit()
            except Exception as error:
                # 出现错误时打印错误日志
                print(error)
            return item

        elif isinstance(item, items.DownloadItem):
            try:
                self.cursor.execute(
                    """select * from t_movies_to_downloadurls where movieId = %s""",
                    item['movieId'])
                # 是否有重复数据
                repetition = self.cursor.fetchone()
                # 重复
                if repetition:
                    pass
                # 插入数据
                else:
                    self.cursor.execute(
                        """insert into t_movies_to_downloadurls(
                                              movieId, 
                                              downloadUrl, 
                                              size, 
                                              clear, 
                                              createTime, 
                                              cili_from
                                              )
                  value (%s, %s, %s, %s, %s, %s)""",
                        (item['movieId'],
                         item['downloadUrl'],
                         item['size'],
                         item['clear'],
                         item['createTime'],
                         item['cili_from'],
                         ))
                    self.cursor.execute('update t_movies set download_url=%s where id=%s',
                                        (item['downloadUrl'],
                                         item['movieId']))
                    # 提交sql语句
                    self.connect.commit()

            except Exception as e:
                print(e)
            return item


class MovieImagesPipeline(ImagesPipeline):
    """图片储存管道"""

    def get_media_requests(self, item, info):
        if isinstance(item, items.MovieItem):
            for url in item['image_urls']:
                yield scrapy.Request(url)
        else:
            pass

    def item_completed(self, results, item, info):
        if isinstance(item, items.MovieItem):
            path = settings.IMAGES_STORE
            image_path = [x['path'] for ok, x in results if ok]
            project_dir = os.path.abspath(os.path.dirname(__file__))
            goal_path = os.path.join(project_dir, 'images')  # 获取保存路径绝对位置
            if not os.path.exists(goal_path):  # 如果不存在则创建
                os.mkdir(goal_path)
            if image_path:
                if shutil.move(os.path.join(path, image_path[0]), goal_path):  # 移动图片至
                    item["local_img_url"] = goal_path
            else:
                item['local_img_url'] = ''
            return item
        else:
            pass


class MoviePipeline(object):
    def process_item(self, item, spider):
        return item
