# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GuaziProItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 通过车源号进行去重
    car_id = scrapy.Field()
    car_name = scrapy.Field()
    # 从哪个连接抓取过来的数据
    from_url = scrapy.Field()
    car_price = scrapy.Field()
    km_info = scrapy.Field()
    # 上牌地
    license_location = scrapy.Field()
    # 排量信息
    desplacement_info = scrapy.Field()
    # 变速箱，手动挡还是自动挡
    transmission_case = scrapy.Field()
