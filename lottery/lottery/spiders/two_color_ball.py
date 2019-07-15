import scrapy
import math, re, os, sys

path = os.getcwd()
sys.path.append(path + '/lottery/spiders/')
from dba import DBA

class LotterySpider(scrapy.Spider):  # 继承scrapy.Spider类
    name = "two_color_ball"  # 蜘蛛名
    url_tpl = 'http://kaijiang.zhcw.com/zhcw/html/ssq/list_%s.html'
    dba = ''
    max_period = 0
    need_compare = False

    def start_requests(self):
        self.dba = DBA()
        self.db_max_period = self.dba.get_max_period()
        yield scrapy.Request(self.url_tpl % '1', callback=self.get_sum)

    # 获取总记录数，计算出总页数，并打开第一页的中的50条详情记录、循环获取2-count页中的数据
    def get_sum(self, response):
        page_count = response.css('.pg strong::text').extract_first()
        page_count = int(page_count)

        # 找到第一页中的最大、最小期数，和数据库中的最大期数比较，
        # 如果等于页面最大期数，不请求数据
        # 如果在此范围，不再请求其他页数据
        # 如果不在此范围，请求全部数据做判断

        db_max_period = self.db_max_period
        trs = response.css('tr')
        tr_len = len(trs)
        tds = trs[2].css('td')
        max_period = int(tds[1].css('::text').extract_first())
        tds = trs[tr_len - 2].css('td')
        min_period = int(tds[1].css('::text').extract_first())

        if max_period == db_max_period:
            return
        elif min_period < db_max_period and db_max_period < max_period:
            self.need_compare = True
            self.get_list(response)
            return

        self.dba.clear()
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
            period = tds[1].css('::text').extract_first()

            if self.need_compare and int(period) <= self.db_max_period:
                continue

            data['period'] = period
            balls = tds[2].css('em::text').extract()
            len1 = len(balls)
            idx = 0
            for num in balls:
                idx += 1
                data['num'] = num
                data['type'] = int(len1 == idx)
                self.dba.insert(data)
