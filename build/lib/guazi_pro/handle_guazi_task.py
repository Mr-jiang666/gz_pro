import requests
#通过execjs这个包，来解析js.安装时安装pyexecjs,pip install pyexecjs
import execjs
import re
from .handle_mongo import mongo

#我们请求城市的接口
url = 'https://www.guazi.com/www/buy'

#cookie值要删掉，否则对方会根据这个值发现我们，并且屏蔽我们
#要通过正则表达式处理请求头,里面有空格，大家一定要注意
header = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Connection":"keep-alive",
    "Host":"www.guazi.com",
    "Referer":"https://www.guazi.com/www/buy",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3610.2 Safari/537.36",
}

response = requests.get(url=url,headers=header)
#设置返回的编码
response.encoding = 'utf-8'
if '正在打开中,请稍后' in response.text:
    #通过正则表达式获取了相关的字段和值
    value_search = re.compile(r"anti\('(.*?)','(.*?)'\);")
    string = value_search.search(response.text).group(1)
    key = value_search.search(response.text).group(2)
    #读取，我们破解的js文件
    with open('guazi.js','r') as f:
        f_read = f.read()
    #使用execjs包来封装这段JS,传入的是读取后的js文件
    js = execjs.compile(f_read)
    js_return = js.call('anti',string,key)
    cookie_value = 'antipas='+js_return
    # print(cookie_value)
    header['Cookie'] = cookie_value
    response_second = requests.get(url=url,headers=header)
    # print(response_second.text)
    city_search = re.compile(r'href="(.*?)/buy" title=".*?">(.*?)</a>')
    brand_search = re.compile(r'href="\/www\/(.*?)\/c-1/#bread"\s+>(.*?)</a>')
    city_list = city_search.findall(response_second.text)
    brand_list = brand_search.findall(response_second.text)
    for city in city_list:
        # if city[1] == '北京':
            for brand in brand_list:
                info = {}
                #https://www.guazi.com/anqing/buy
                #https://www.guazi.com/anqing/audi/#bread
                #https://www.guazi.com/anqing/audi/o1i7/#bread
                info['task_url'] = 'https://www.guazi.com'+city[0]+'/buy/i7/'+brand[0]
                info['city_name'] = city[1]
                info['brand_name'] = brand[1]
                info['item_type'] = 'list_item'
                # print(info)
                #保存到mongodb里面去
                mongo.save_task('guazi_task',info)

