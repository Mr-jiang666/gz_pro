# -*- coding: utf-8 -*-
import re

import scrapy

from guazi_pro.handle_mongo import mongo
from guazi_pro.items import GuaziProItem


class GzProSpider(scrapy.Spider):
    name = 'gz_pro'
    allowed_domains = ['guazi.com']
    # start_urls = ['http://guazi.com/']

    def start_requests(self):
        while True:
            task = mongo.get_task('guazi_task')
            # task取空了，就停下来
            if not task:
                break
            if '_id' in task:
                task.pop('_id')
            print('当前获取到的task为：%s' % task)
            if task['item_type'] == 'list_item':
                # 这个request对象代表了一个http的请求
                # 会经由downloader去执行，从而产生一个response
                yield scrapy.Request(
                    # 发送请求的URL
                    url=task['task_url'],
                    dont_filter=True,
                    callback=self.handle_car_item,
                    errback=self.handle_err,
                    meta=task
                    # callback回调函数，默认不写会调用parse方法
                    # 请求方法，默认为get
                    # method='GET',
                    # 请求头信息
                    # headers=
                    # body=请求体
                    # cookies=要携带的cookie信息
                    # meta=是字典的格式，向其他方法里面传递信息
                    # encoding='utf-8'字符编码
                    # priority=0请求的优先级
                    # dont_filter=False这个请求是否要被过滤
                    # errback=self.handle_err,当程序处理请求返回有错误的时候，使用这个参数
                    # flags
                )
                # 是用来发送POST表单请求所使用的方法
                # yield scrapy.FormRequest()
            elif task['item_type'] == 'car_info_item':
                yield scrapy.Request(url=task['car_url'], callback=self.handle_car_info, dont_filter=True, meta=task,
                                     errback=self.handle_err)

    # 报错回调方法
    def handle_err(self, failure):
        print(failure)
        # failure.request.meta,来获取到失败的task
        # 把失败的请求扔会task库
        mongo.save_task('guazi_task', failure.request.meta)

    # 自定义的解析方法
    def handle_car_item(self, response):
        if '中为您找到0辆好车' in response.text:
            return
        # 当前页面所展示的二手车,item
        car_item_list = response.xpath("//ul[@class='carlist clearfix js-top']/li")
        for car_item in car_item_list:
            # 创建一个字典用于存储二手车的名称和详情页的url
            car_list_info = {}
            # scrapy xpath返回是一个列表,extract_first获取索引为0的值
            car_list_info['car_name'] = car_item.xpath("./a/h2/text()").extract_first()
            car_list_info['car_url'] = 'https://www.guazi.com' + car_item.xpath("./a/@href").extract_first()
            car_list_info['item_type'] = 'car_info_item'
            yield scrapy.Request(url=car_list_info['car_url'], callback=self.handle_car_info, dont_filter=True,
                                 meta=car_list_info, errback=self.handle_err)

        # 写到for循环的外面
        if response.xpath("//ul[@class='pageLink clearfix']/li[last()]//span/text()").extract_first() == '下一页':
            info2 = {}
            # https://www.guazi.com/bj/audi-a8l/o1i7/
            value_search = re.compile("https://www.guazi.com/(.*?)/(.*?)/o(\d+)i7")
            # 返回的是列表，列表里面包含的是元组
            try:
                value = value_search.findall(response.url)[0]
                # 下一页连接,response.request.meta字典的值覆盖了
                response.request.meta['task_url'] = 'https://www.guazi.com/%s/%s/o%si7' % (
                    value[0], value[1], str(int(value[2]) + 1))
                # callback要调用handle_car_item
                yield scrapy.Request(url=response.request.meta['task_url'], callback=self.handle_car_item,
                                     meta=response.request.meta, dont_filter=True, errback=self.handle_err)
            except:
                print('11111111111', response.url)

    # 解析二手车详情页
    def handle_car_info(self, response):
        # 获取到列表页里面的二手车的名称，以及二手车的URL
        # 通过车源号进行去重,通过正则表达式,车源号：HC-73829610
        car_id_search = re.compile(r"车源号：(.*?)\s+")
        # 创建items内部定义的字段的实例
        car_info = GuaziProItem()
        # car_id
        car_info['car_id'] = car_id_search.search(response.text).group(1)
        # 通过meta传递过来的car_name
        car_info['car_name'] = response.request.meta['car_name']
        # 从哪个连接抓取过来的数据
        car_info['from_url'] = response.request.meta['car_url']
        # strip()用来去除空格的
        car_info['car_price'] = response.xpath("//span[@class='price-num']/text()").extract_first().strip()
        car_info['km_info'] = response.xpath(
            "//ul[@class='assort clearfix']/li[@class='two']/span/text()").extract_first().strip()
        # 上牌地
        car_info['license_location'] = \
        response.xpath("//ul[@class='assort clearfix']/li[@class='three']/span/text()").extract()[0].strip()
        try:
            # 排量信息
            car_info['desplacement_info'] = \
            response.xpath("//ul[@class='assort clearfix']/li[@class='three']/span/text()").extract()[1].strip()
        except:
            car_info['desplacement_info'] = "不存在"
        # 变速箱，手动挡还是自动挡
        car_info['transmission_case'] = response.xpath(
            "//ul[@class='assort clearfix']/li[@class='last']/span/text()").extract_first().strip()
        yield car_info
