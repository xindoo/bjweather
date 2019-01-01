# -*- coding: utf-8 -*-
import scrapy
import re

# 这个网站数据中加了好多换行和其他字符， 需要转换下才能用
invisibleChar = re.compile(r'[\s]+')
nonDigit = re.compile(r'[^\d]+')
digit = re.compile(r'([-\d]+)[^-\d]+([-\d]+)')

class GetdataSpider(scrapy.Spider):
    usedUrl = set()  # 用一个set保存已经爬取过的数据url  
    url = 'http://www.tianqihoubao.com'
    name = 'getdata'
    allowed_domains = ['www.tianqihoubao.com']
    start_urls = ['http://www.tianqihoubao.com/lishi/beijing/month/201812.html']

    def parse(self, response):
        trs = response.xpath('//tr')
        isFirst = True
        for tr in trs:
            if isFirst:
                isFirst = False
                continue
            tds = tr.xpath('./td')
            temperature = re.sub(invisibleChar, "",tds[2].xpath('./text()').extract()[0])
            maxT = digit.match(temperature).group(1)
            minT = digit.match(temperature).group(2)
            date = re.sub(invisibleChar, "",tds[0].xpath('./a/text()').extract()[0])
            date = re.sub(nonDigit, '-', date)[0:-1]
            yield {
                "date":date,
                "maxT":maxT,  # 最大温度
                "minT":minT,  # 最小温度 
                "weather":re.sub(invisibleChar, "",tds[1].xpath('./text()').extract()[0]),  # 天气情况
                "wind":re.sub(invisibleChar, "",tds[3].xpath('./text()').extract()[0])  # 风力等级 
            }
        nextUrls = response.xpath('//div[@class="months"]/a/@href')
        self.usedUrl.add(response.url)
        for nextUrl in nextUrls: 
            url = self.url+nextUrl.extract()
            if url in self.usedUrl:
                continue   # 爬过的就不爬了  
            yield scrapy.Request(url, callback=self.parse)
            break

