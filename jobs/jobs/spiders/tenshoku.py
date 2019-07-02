import scrapy
import math, re, os, sys

path = os.getcwd()
# print(path)
sys.path.append(path + '/jobs/spiders/')
from dba import DBA2

class JobOperator2(scrapy.Spider):  # 继承scrapy.Spider类
    # 测试相关
    debug = False
    debug_len = 10  # 测试数量

    # 正常变量
    name = "tenshoku"  # 蜘蛛名
    page_size = 50  # 每页50条记录
    url_tpl = 'https://tenshoku.mynavi.jp/search/list/?pageNo='
    index = 0
    dba = DBA2()

    def start_requests(self):
        # yield scrapy.Request(self.url_tpl + '1', callback=self.get_sum)
        pass

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'token': '156205906600080b8c87f505e34b886a8f83c11898672f348cc6ccc8f9c857cb1c476101932b8',
                      # 'srOccCdList': '16',
                      'srOccCdList': '1G',
                      'srFreeSearchCd': '4',
                      'jobsearchType': '4',
                      'searchType': '8'},
            callback=self.get_sum
        )

    # 获取总记录数，计算出总页数，并打开第一页的中的50条详情记录、循环获取2-count页中的数据
    def get_sum(self, response):
        count = response.css('.rnn-pageNumber.rnn-textLl::text').extract_first()
        page_count = math.ceil(int(count) / self.page_size)

        for n in range(-1, page_count):
            if self.debug and n > page_count - 2: break  # debug 时只取第一页
            no = str(self.page_size * n + 1)
            res_url = self.url_tpl + no
            yield scrapy.Request(url=res_url, callback=self.get_list)

    def write_log(self, cont):
        fileName = './logs.txt'
        with open(fileName, "a+") as f:  # “a+”以追加的形式
            f.write(cont)
            f.write('\n')
            f.close()
