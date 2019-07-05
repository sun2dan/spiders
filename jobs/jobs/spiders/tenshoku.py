import scrapy
import math, re, os, sys, random, time

path = os.getcwd()
# print(path)
sys.path.append(path + '/jobs/spiders/')
from dba2 import DBA2

class JobOperator2(scrapy.Spider):  # 继承scrapy.Spider类
    # 测试相关
    debug = False
    debug_len = 2  # 测试数量

    # 正常变量
    name = "tenshoku"  # 蜘蛛名
    page_size = 50  # 每页50条记录
    url_tpl = 'https://tenshoku.mynavi.jp/search/list/?pageNum='
    index = 0
    formdata = {
        'token': '15621077260008687d73c2611519694229fd107f1c82dda8c52a5c5920734aad4847b619916ac',
        # 'srOccCdList': '16',
        'srOccCdList': '16,1G',
        'srFreeSearchCd': '4',
        'jobsearchType': '4',
        'searchType': '8'
    }
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

    dba2 = DBA2()

    def start_requests(self):
        yield scrapy.FormRequest(self.url_tpl + '1',
                                 formdata=self.formdata, cookies=self.cookies,
                                 callback=self.get_sum)

    # 获取总记录数，计算出总页数，并打开第一页的中的50条详情记录、循环获取2-count页中的数据
    def get_sum(self, response):
        count = response.css('.result__num em::text').extract_first()
        page_count = math.ceil(int(count) / self.page_size)

        for n in range(1, page_count + 1):
            if self.debug and n > 2: break  # debug
            res_url = self.url_tpl + str(page_count + 1 - n)
            time.sleep(1)
            yield scrapy.FormRequest(res_url, formdata=self.formdata, cookies=self.cookies,
                                     callback=self.get_list)

        # for n in [1]:
        #     if self.debug and n > 2: break  # debug
        #     res_url = self.url_tpl + str(n)
        #     yield scrapy.FormRequest(res_url, formdata=self.formdata, cookies=self.cookies,
        #                              callback=self.get_list)

    def get_list(self, response):
        idx = 0
        urls1 = response.css('.cassetteRecruitRecommend__copy a::attr(href)').extract()  # 注目
        urls = response.css('.cassetteRecruit__copy a::attr(href)').extract()  # 普通
        for item in urls + urls1:
            if self.debug and idx >= self.debug_len:
                break
            detail_url = 'https://tenshoku.mynavi.jp' + item
            format_url = re.sub(r'(\/msg\/)|(\/adv1\/)|(\\+)', '\/', detail_url)
            format_url = re.sub(r'\\+', '', format_url)
            idx += 1
            yield scrapy.Request(url=format_url, callback=self.get_detail)

    def get_detail(self, response):
        data = self.dba2.get_empty_obj()

        table = response.css('.jobOfferTable')[0]
        theads = table.css('th.jobOfferTable__head::text').extract()  # .re(r'[\s\S]+')  # 标题
        conts = table.css('td.jobOfferTable__body').re(r'<p[\s\S]+</p>')  # 内容

        if len(theads) != len(conts):
            msg = '招聘信息表格数量不对，当前url：%s' % response.url
            self.write_log(msg)
            return print(msg)

        data['url'] = response.url
        data['ntype'] = 'ten'
        data['title'] = response.css('.cassetteOfferRecapitulate__job span::text').extract_first()
        # 招聘时间
        during = response.css('.cassetteOfferRecapitulate__date').re('<p[\s\S]+</p>')[0]
        pattern = re.compile(r'\d{4}\/\d{2}\/\d{2}', re.M | re.I)
        ms = pattern.findall(str(during))
        if len(ms) > 0:
            data['during'] = '{0}～{1}'.format(ms[0], ms[1])
        # 标签
        tags = response.css('.jobOfferInfo__labelFeature span::text').extract()
        data['tags'] = ','.join(tags)
        # 公司
        company = response.css('.cassetteOfferRecapitulate__content p.text::text').extract_first()
        data['company'] = self.format_cont(company.split('|')[0])

        fields = {
            '仕事内容': 'content',  # 工作内容 - - 仕事の内容
            '求める人材': 'claim',  # 任职要求 - - 求めている人材
            '勤務地': 'addr',  # 工作地点 - - 勤務地
            '給与': 'salary',  # 工资 - - 給与
            '勤務時間': 'worktime',  # 上班时间 - - 勤務時間
            '休日・休暇': 'holiday',  # 休假信息 - - 休日・休暇
            '福利厚生': 'welfare',  # 福利 - - 待遇・福利厚生
            -1: 'desc'  # 其他字段放到备注中
        }

        idx = -1
        desc_arr = []  # 除了默认7个字段之外的字段
        for head in theads:
            idx += 1
            key = fields.get(head, '')
            cont = conts[idx]
            if key == 'salary':
                cont = re.sub(r'<em[\s\S]+</span>', '', cont)
            format_cont = self.format_cont(cont)

            if key:
                data[key] = format_cont
            else:  # 额外的内容
                desc_arr.append(
                    '<div>{0}##{1}</div>'.format(re.sub(r'\s+', '', head), format_cont))

        data['desc'] = ''.join(desc_arr)

        self.dba2.insert(data)

    # 内容格式化
    def format_cont(self, cont):
        s1 = re.sub(r'(\s+)|(<p[\s\w_=\-\'\"]+>)', '', cont)  # 去空格  # re.sub(r'</?\w+>', '', s3) # 去所有标签
        s2 = re.sub(r'</p>', '<br>', s1)  # 内部p结束标签替换成br
        s3 = re.sub(r'(<br/?>)+', '<br>', s2)  # 多个br合并 <br><br>
        s4 = re.sub(r"'", "''", s3)  # 单引号替换
        return s4

    def write_log(self, cont):
        pass
        fileName = './logs2.txt'
        with open(fileName, "a+") as f:  # “a+”以追加的形式
            f.write(cont)
            f.write('\n')
            f.close()
