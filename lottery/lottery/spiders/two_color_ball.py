import scrapy
import math, re, os, sys

path = os.getcwd()
# print(path)
sys.path.append(path + '/lottery/spiders/')
from dba import DBA

class JobOperator(scrapy.Spider):  # 继承scrapy.Spider类
    name = "two_color_ball"  # 蜘蛛名
    url_tpl = 'http://kaijiang.zhcw.com/zhcw/html/ssq/list_%s.html'
    dba = ''

    def start_requests(self):
        self.dba = DBA()
        yield scrapy.Request(self.url_tpl % '1', callback=self.get_sum)

    # 获取总记录数，计算出总页数，并打开第一页的中的50条详情记录、循环获取2-count页中的数据
    def get_sum(self, response):
        page_count = response.css('.pg strong::text').extract_first()
        page_count = int(page_count)
        self.get_list(response)

        for n in range(2, page_count):
            res_url = self.url_tpl % n
            yield scrapy.Request(url=res_url, callback=self.get_list)

    # 获取一级页面，包含分页数据的列表页面
    def get_list(self, response):
        trs = response.css('tr')
        data = self.dba.get_empty_obj()

        for tr in trs:
            tds = tr.css('td')
            if len(tds) != 7: continue
            data['period'] = tds[1].css('::text').extract_first()
            balls = tds[2].css('em::text').extract()
            len1 = len(balls)
            idx = 0
            for num in balls:
                idx += 1
                data['num'] = num
                data['type'] = int(len1 == idx)
                self.dba.insert(data)
