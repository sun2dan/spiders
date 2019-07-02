import scrapy
import math, re, os, sys

path = os.getcwd()
# print(path)
sys.path.append(path + '/jobs/spiders/')
from dba2 import DBA2

class JobOperator2(scrapy.Spider):  # 继承scrapy.Spider类
    # 测试相关
    debug = False
    debug_len = 10  # 测试数量

    # 正常变量
    name = "tenshoku"  # 蜘蛛名
    page_size = 50  # 每页50条记录
    url_tpl = 'https://tenshoku.mynavi.jp/search/list/?pageNum=3'
    index = 0
    dba = DBA2()

    def start_requests(self):
        formdata = {
            'token': '15621077260008687d73c2611519694229fd107f1c82dda8c52a5c5920734aad4847b619916ac',
            #'srOccCdList': '16',
            'srOccCdList': '16,1G',
            'srFreeSearchCd': '4',
            'jobsearchType': '4',
            'searchType': '8'
        }
        headers = {}
        cookies = {
            'SSID': '77191b0a1c2a6ea27e2630493a2d197fa0b0d796',
            'TRACKING_ID': 'rO0ABXQAJDViNWJlNGY2LTNjYzItNDVmMS04NDVjLWFlMGZmM2IyYmE1NA%3D%3D',
            '_ga': 'GA1.2.1144375011.1543886684', 'krt.vis': '22053685_1543886920336_682134640',
            '_ga': 'GA1.3.1144375011.1543886684', '__gunoad': 'b4dd9131-e15d-4a7f-8b68-4af8650107d2',
            '_rt.uid': '683f52c0-f768-11e8-ce51-06c4de00373a', 'snexid': '8bc03b24-fa15-4e5b-82f0-b29d5d1814fb',
            '_tdim': '3af5f71e-d5be-420d-bbaf-9aa239a4b79d', 'visitor_id92712': '440691943',
            'visitor_id92712-hash': '8c5961cc3f8adcd5545538944c407d67f3d31d9d2ee027386a8158a445838fa257f72de1cbfc4b4300c2296a3f7423dc35f89a30',
            'cto_lwid': 'e0f9d72e-07ea-4754-aa0f-a5778eeaa78a', '_fbp': 'fb.1.1561359387554.752698291',
            'BIGipServertnwebap_80_pool': '1512577452.20480.0000', '_gid': 'GA1.2.1932280237.1562058924',
            'BIGipServertnweb_8008_pool': '556276140.18463.0000', 'xyz_cr_144_et_100': 'NaN&cr=144&et=100',
            'Apache': '111.200.23.40.1562059098720716', 'BIGipServertnweb_80_pool': '539498924.20480.0000',
            'adlpo': 'PC#1556583681828-944104-454345#1569837967|check#true#1562062026',
            '_adp_uid': 'BwCFEgAKkQHMIWfQ5XYEN_KTTzP88HFx', 'JSESSIONID': '4EF398E4B0D1CFE1937D32BE835D09F9',
            '_dc_gtm_UA-23072088-3': '1', '_dc_gtm_UA-23072088-1': '1', '_dc_gtm_UA-23072088-2': '1'
        }

        yield scrapy.FormRequest(self.url_tpl,
                                 formdata=formdata, headers=headers, cookies=cookies,
                                 callback=self.get_sum)

    def parse(self, response):
        return
        return scrapy.FormRequest.from_response(
            response,
            formdata={'token': '156205906600080b8c87f505e34b886a8f83c11898672f348cc6ccc8f9c857cb1c476101932b8',
                      # 'srOccCdList': '16',
                      'srOccCdList': '16,1G',
                      'srFreeSearchCd': '4',
                      'jobsearchType': '4',
                      'searchType': '8'},
            callback=self.get_sum
        )

    # 获取总记录数，计算出总页数，并打开第一页的中的50条详情记录、循环获取2-count页中的数据
    def get_sum(self, response):
        count = response.css('.result__num em::text').extract_first()
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
