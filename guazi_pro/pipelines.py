# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from .handle_mongo import mongo


class GuaziProPipeline:
    def process_item(self, item, spider):
        mongo.save_data('guazi_data',item)
        return item
