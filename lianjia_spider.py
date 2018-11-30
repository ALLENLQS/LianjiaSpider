# -*- coding: utf-8 -*-
# @Author  : ALLEN
# @Time    : 2018/8/30 21:26
# @File    : lianjia_spider0830.py
# @Software: PyCharm
from lxml import etree
from urllib import request
import threading
broker_namedata = []
house_namedata = []
broker_data = []
def getHouse(addr,pg):
    pg = int(pg)
    if pg == 1:
        url = "https://cd.lianjia.com/zufang/%s/"%addr
        Referer = "https://cd.lianjia.com/zufang/"
    elif pg == 2:
        url = "https://cd.lianjia.com/zufang/%s/pg%s/" % (addr, pg)
        Referer = "https://cd.lianjia.com/zufang/%s/" % addr
    else:
        url = "https://cd.lianjia.com/zufang/%s/pg%s" % (addr, pg)
        Referer = "https://cd.lianjia.com/zufang/%s/pg%s" % (addr, pg-1)
    headers = {
        "Referer": Referer,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
    }
    req = request.Request(url = url,headers = headers)
    # 这里的urlopen打开的是一个对象
    response = request.urlopen(req)
    # 对爬取到的网页信息进行读取和解码
    result = response.read().decode("utf-8")
    # 用xpath构建html匹配的对象
    html = etree.HTML(result)
    # 第一步匹配房屋信息的主div
    house_list = html.xpath('//ul[@id="house-lst"]/li/div[@class="info-panel"]')
    # report_dict = {}
    for house in house_list:
        # 当前的house就是一个xpath对象
        house_name = house.xpath('h2/a')[0]  # 注意，xpath匹配哪怕一个返回的也是列表
        name = house_name.text.strip()
        # 然后进行样式、大小、和地址的匹配，我们称这个匹配为房屋的描述
        # 房屋样式匹配
        house_description = house.xpath('div[@class="col-1"]')[0]
        house_style = house_description.xpath('div[@class="where"]/span[@class="zone"]/span')[0]
        style = house_style.text.strip()
        # 房屋大小匹配
        house_size = house_description.xpath('div[@class="where"]/span[@class="meters"]')[0]
        size = house_size.text.strip()
        # 房屋地址匹配
        house_address = house_description.xpath('div[@class="other"]/div[@class="con"]/a')[0]
        address = house_address.text.strip()
        # 然后进行价格匹配
        house_price = house.xpath('div[@class="col-3"]/div[@class="price"]/span')[0]
        price = house_price.text.strip()
        # 获取经纪人信息地址
        broker_list = house.xpath('h2/a/@href')[0]
        # print(broker_list)
        # 这里调用一个函数，此函数能够获得经纪人的姓名和联系方式
        broker_name,broker_phone = getBroker(broker_list,url)
        # 进行信息的汇总
        result_dict = {
            "address": address,
            "name": name,
            "style": style,
            "size": size,
            "price": price,
            "broker_name":broker_name,
            "broker_phone": broker_phone
        }
        # 经纪人信息
        broker_dict = {
            "broker_name":broker_name,
            "address":address
        }
        content = "%(address)s--->%(name)s--->[%(style)s]--->面积:%(size)s--->价格:%(price)s--->经纪人:%(broker_name)s " \
                  "--->联系方式:%(broker_phone)s" % result_dict
        print(content)
        broker_namedata.append(result_dict["broker_name"])
        house_namedata.append(result_dict["name"])
        broker_data.append(broker_dict)
        report_dict = {}
        if broker_name in report_dict:
            if address in report_dict:
                report_dict[address]['num'] += 1
                report_dict[address]['house'].append(result_dict)
            else:
                report_dict[address] = {"num": 0, "house": [result_dict]}
            print(report_dict)
def getBroker(broker_list,url):
    broker_headers = {
        "Referer": url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
    }
    broker_req = request.Request(url=broker_list, headers=broker_headers)
    broker_response = request.urlopen(broker_req)
    broker_result = broker_response.read().decode('utf-8')
    broker_html = etree.HTML(broker_result)
    try:
        broker_name = broker_html.xpath('//div[@class="brokerName"]/a/text()')[0].strip()
        broker_phone = broker_html.xpath('//div[@class="phone"]/text()')[0].strip() + ' 转 ' +broker_html.xpath('//div[@class="phone"]/text()')[1].strip()
    except Exception:
        broker_name = '暂无相关经纪人'
        broker_phone = '请直接联系客服 10109666'
    return broker_name,broker_phone
def getStatistics():
    """
    首先需要将经纪人姓名存在一个列表中，方便我们去取出，有多少次就有多少套房产
    再将每个人的负责的房产信息得出一个列表，取出多少次就有多少个经纪人
    按照每个人负责的房产数量排序（降序）
    判断最有可能在的位置，需要将每个人负责的房产的位置进行统计，排在第一位的地址就是经纪人最有可能的位置
    :return:
    """
    # 房产数量
    house_number = 0
    # 经纪人数量
    broker_number = 0
    # 存放经纪人负责的房产
    count = {}
    # 存放经纪人负责的房产位置
    for broker in broker_namedata:
        # 统计该区域有多少房产
        house_number += 1
        # 统计每个经纪人负责的房产数量
        count[broker] = count.get(broker,0) + 1
        # 对经纪人负责的房产数量进行排序
        sorted_count = sorted(count.items(),key=lambda x:x[1],reverse=True)
    for count[broker]  in count:
        # 统计该区域有多少经纪人
        broker_number += 1
    print('=========='*10)
    print("经纪人负责的房产数量如下:%s \n当前查询总共有%s套房产\n当前查询经纪人总共%s人"%(count,house_number,broker_number))
    print('==========' * 10)
    print("排名前十情况如下:")
    print('==========' * 10)
    for i in range(1,11):
        print("第%d名:%s\n此经纪人可能住在:xxx附近" % (i,sorted_count[i-1]))
    print(broker_data)
# 对房产信息进行逐页显示
def getResult(addr,page):
    for i in range(1,int(page+1)):
        print('++++++++++'*5 + "这是%s第%s页房产信息"%(addr,i) + '++++++++++'*5)
        getHouse(addr,i)
    # 调用统计信息函数
    getStatistics()

if __name__ == "__main__":
    # getHouse("gaoxin7", 5)
    # getResult('gaoxin7',5)
    t1 = threading.Thread(target=getResult,args=('gaoxin7',5))
    t1.start()