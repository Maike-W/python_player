# -*- coding: utf-8 -*-
import re

import scrapy

from fang.items import NewHouseItem,ESFHouseItem
from scrapy_redis.spiders import RedisSpider

class SfwSpider(RedisSpider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = "fang:start_urls"

    def parse(self, response):
        trs = response.xpath("//div[@class='outCont']//tr")
        province = None
        for tr in trs:
            tds = tr.xpath(".//td[not(@class)]")
            province_td = tds[0]
            province_text = province_td.xpath(".//text()").get()
            province_text = re.sub(r"\s", "", province_text)
            if province_text:
                province = province_text
            # 不爬去海外的房地产信息
            if province == "其它":
                continue
            city_td = tds[1]
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                # print("省份:",province)
                # print("城市:",city)
                # print("城市链接:",city_url)
                # 构建新房链接
                url_module = city_url.split("//")
                scheme = url_module[0]
                domainall = url_module[1].split(".")
                domain_city = domainall[0]
                domain_fang = domainall[1]
                domain_com = domainall[2]
                if domain_city == 'bj':
                    newhouse_url = "https://newhouse.fang.com/"
                    esf_url = "https://esf.fang.com/"
                else:
                    newhouse_url = scheme + "//" + domain_city + "." + "newhouse" + "." + domain_fang + "." + domain_com + "house/s/"
                    # 构建二手房链接
                    esf_url = scheme + "//" + domain_city + "." + "esf" + "." + domain_fang + "." + domain_com
                # print("城市:%s,%s"%(province,city))
                # print('新房链接:%s'%(newhouse_url))
                # print('二手房链接:%s'%(esf_url))
                yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse,
                                     meta={"info": (province, city, newhouse_url)})

                yield scrapy.Request(url=esf_url, callback=self.parse_esf,
                                     meta={"info": (province, city)})
                break
            break

    def parse_newhouse(self, response):
        province, city, newhouse_url = response.meta.get("info")
        # print(newhouse_url)
        lis = response.xpath("//div[@class='nl_con clearfix']/ul/li")
        for li in lis:
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            if name == None:
                continue
            name = name.strip()
            # print(name)
            house_type_text = li.xpath(".//div[@class='house_type clearfix']/a/text()").getall()
            house_type_text = list(map(lambda x: re.sub(r"\s", "", x), house_type_text))
            rooms = list(filter(lambda x: x.endswith("居"), house_type_text))
            # print(rooms)
            area = "".join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall())
            area = re.sub(r"\s|－|/", "", area)
            # print(area)
            # district=li.xpath("")
            address = li.xpath(".//div[@class='address']/a/@title").get()
            # print(address)
            district_text = "".join(li.xpath(".//div[@class='address']/a//text()").getall())
            district = re.search(r".*\[(.+)\].*", district_text).group(1)
            # print(district)
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            # print(sale)
            price = "".join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price = re.sub(r"\s|广告", "", price)
            # print(price)
            origin_url = "".join(li.xpath(".//div[@class='nlcd_name']/a/@href").get())
            origin_url = "https:" + origin_url
            # print(origin_url)
            item = NewHouseItem(name=name, rooms=rooms, area=area, address=address, district=district, sale=sale,
                                price=price, origin_url=origin_url, province=province, city=city)
            yield item

        next_url = "".join(response.xpath("//div[@class='page']//a[@class='next']/@href").get())
        next_url = newhouse_url + next_url
        # print(next_url)
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_newhouse,meta={"info": (province, city, newhouse_url)})



    def parse_esf(self, response):
        province, city = response.meta.get("info")
        dls=response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            item=ESFHouseItem(province=province,city=city)
            item["name"]=dl.xpath(".//p[@class='add_shop']/a/@title").get()
            infos=dl.xpath(".//dd/p[@class='tel_shop']/text()").getall()
            infos=list(map(lambda x:re.sub(r"\s","",x),infos))
            # print(infos)
            # print(name)
            for info in infos:
                if "厅" in info:
                    item['rooms']=info
                elif "层" in info:
                    item["floor"]=info
                elif "向" in info:
                    item["toward"]=info
                elif "年" in info:
                    item["year"]=info.replace("建","")
                else:
                    item["area"]=info
                # print(item)
            address=dl.xpath(".//p[@class='add_shop']/span/text()").get()
            # print(address)
            item['address'] = address
            item['price'] =dl.xpath(".//dd[@class='price_right']/span/text()").getall()
            item['unit']=dl.xpath(".//dd[@class='price_right']/span[1]/text()").getall()
            detail_url=dl.xpath(".//dd//h4[@class='clearfix']/a/@href").get()
            item['origin_url']=response.urljoin(detail_url)
            # print(item['origin_url'])
            yield item
        next_url=response.xpath(".//div[@class='page_al']/p[1]/a/@href").get()
        yield scrapy.Request(url=response.urljoin(next_url),callback=self.parse_esf,meta={"info":(province,city)})
