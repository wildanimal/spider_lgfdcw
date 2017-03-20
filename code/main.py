# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding("utf-8")
import pymongo
import urllib2
import re
from bs4 import BeautifulSoup

dbserv = pymongo.MongoClient('localhost', 27017)

db = dbserv["lgfdcw"]
coll = db["house_info"]

req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
'Accept':'text/html;q=0.9,*/*;q=0.8',
 'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
# 'Accept-Encoding':'gzip',
'Connection':'close',
'Referer': None #注意如果依然不能抓取的话，这里可以设置抓取网站的host
}

# 可改成函数这里就懒的写了
for i in range(1, 2000):
    # 网站URL
    urlxx = "http://www.lgfdcw.com/cs/index.php?userid=&infotype=&dq=&fwtype=&hx=&price01=&price02=&pricetype=&fabuday=&addr=&PageNo=" + str(
        i)
    print(urlxx)
    request = urllib2.Request(urlxx, None, req_header)
    response = urllib2.urlopen(request)
    html = response.read()
    # print(html)
    lj = re.compile('<a href="(.*?)".*?target="_blank"><strong>.*?</strong></a>')
    herflink = re.findall(lj, html)  # 匹配到想要的连接
    print(herflink)
    resultinfo = False  # 定义结束变量
    # 遍历跳转链接，抓取数据。这里可以改成函数，程序可以清晰化。
    for getlink in herflink:
        # 跳转后URL
        url = "http://www.lgfdcw.com/cs/" + str(getlink)
        print(url)
        requset = urllib2.Request(url, None, req_header)
        opencontext = urllib2.urlopen(requset)
        htmlcontext = opencontext.read()
        soup = BeautifulSoup(htmlcontext, "lxml")
        firsttable = soup.find_all('table')[8].find_all('table')[0]  # 第一部分表，其中包含联系人信息
        secondtable = soup.find_all('table')[8].find_all('table')[1]  # 第二部分表，包含房子详细信息
        threetable = soup.find_all('table')[12]  # 第二部分表，房子环境信息（楼层这些）

        fbdt = soup.find(color="#009900").string[5:15]  # 发布时间
        # 存在HTML结构不一致的情况，需异常处理
        try:
            lg = threetable.find_all('tr')[1].find_all('td')[1].get_text()  # 房屋楼层
        except:
            lg = threetable.find_all('tr')[2].find_all('td')[1].get_text()  # 房屋楼层

        contact = firsttable.find_all('tr')[1].find_all('td')[1].get_text()  # 联系人
        data = {
            "phone" : firsttable.find_all('tr')[2].find_all('td')[1].get_text().strip(),  # 联系电话
            "mobile" : firsttable.find_all('tr')[3].find_all('td')[1].get_text().strip(),  # 手机号码
            "address" : firsttable.find_all('tr')[4].find_all('td')[1].get_text().strip(),  # 联系地址
            "seller_props" : secondtable.find_all('tr')[1].find_all('td')[1].get_text().strip(),  # 卖方性质
            "detail_address" : secondtable.find_all('tr')[2].find_all('td')[1].get_text().strip(),  # 详细地址
            "house_type" : secondtable.find_all('tr')[3].find_all('td')[1].get_text().strip(),  # 房屋类型
            "apartment" : secondtable.find_all('tr')[4].find_all('td')[1].get_text().strip(),  # 房屋户型
            "area" : secondtable.find_all('tr')[4].find_all('td')[3].get_text().strip(),  # 房屋面积
            "price" : secondtable.find_all('tr')[5].find_all('td')[1].get_text().strip(),  # 出售价格
            "pay_type" : secondtable.find_all('tr')[5].find_all('td')[3].get_text().strip(),  # 付款方式
            "property" : secondtable.find_all('tr')[6].find_all('td')[1].get_text().strip(),  # 产权性质
            "use_years" : secondtable.find_all('tr')[6].find_all('td')[3].get_text().strip(),  # 使用年限
            "house_props" : secondtable.find_all('tr')[7].find_all('td')[1].get_text().strip(),  # 房屋性质
            "decoration" : secondtable.find_all('tr')[7].find_all('td')[3].get_text().strip(),  # 装修程度
            "house_structor" : secondtable.find_all('tr')[8].find_all('td')[1].get_text().strip(),  # 房屋结构
            "mediate" : secondtable.find_all('tr')[8].find_all('td')[3].string.strip()  # 可否中介
        }
        coll.insert(data)
        

        # resultinfo=true就结束循环
        if resultinfo:
            break
print("执行成功！")
