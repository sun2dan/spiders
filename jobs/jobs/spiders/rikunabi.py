import scrapy
import math, re, os, sys

path = os.getcwd()
# print(path)
sys.path.append(path + '/jobs/spiders/')
from dba import DBA

class JobOperator(scrapy.Spider):  # 继承scrapy.Spider类
    # 测试相关
    debug = False
    debug_len = 10  # 测试数量

    # 正常变量
    name = "rikunabi"  # 蜘蛛名
    page_size = 50  # 每页50条记录
    url_tpl = 'https://next.rikunabi.com/rnc/docs/cp_s00700.jsp?jb_type_long_cd=0500000000&jb_type_long_cd=1200000000&curnum='
    index = 0
    dba = DBA()

    def start_requests(self):
        yield scrapy.Request(self.url_tpl + '1', callback=self.get_sum)

    # 获取总记录数，计算出总页数，并打开第一页的中的50条详情记录、循环获取2-count页中的数据
    def get_sum(self, response):
        count = response.css('.rnn-pageNumber.rnn-textLl::text').extract_first()
        page_count = math.ceil(int(count) / self.page_size)

        for n in range(-1, page_count):
            if self.debug and n > page_count - 2: break  # debug 时只取第一页
            no = str(self.page_size * n + 1)
            res_url = self.url_tpl + no
            yield scrapy.Request(url=res_url, callback=self.get_list)

    # 获取一级页面，包含分页数据的列表页面
    def get_list(self, response):
        idx = 0

        # 获取url和类型
        li = response.css('li.rnn-jobOfferList__item')
        detail_urls = li.css('.rnn-textLl.js-abScreen__title a::attr(href)').extract()
        ntypes = li.css('li::attr(data-ntype)').extract()

        if len(detail_urls) != len(ntypes):
            msg = 'url 和 ntype 长度不匹配，长度分别为：', len(detail_urls), len(ntypes), response.url
            self.write_log(msg)
            return print(msg)

        for url in detail_urls:
            if self.debug and idx >= self.debug_len:
                break
            ntype = ntypes[idx]

            detail_url = response.urljoin(url)
            if ntype == '5':
                detail_url = re.sub(r'\/nx1_', r'/nx2_', detail_url)
                detail_url = re.sub(r'\?[\s\S]+$', r'?leadtc=ngen_tab-top_info', detail_url)
                # res: https://next.rikunabi.com/company/cmi0520246015/nx2_rq0017615082/?leadtc=ngen_tab-top_info
            elif ntype == 't':
                detail_url = re.sub(r'&amp;', '&', detail_url)

            idx += 1
            self.index += 1
            print(self.index, detail_url)

            # 请求二级页面
            yield scrapy.Request(detail_url, self.get_details)  # 发送请求爬取参数内容

    # 从二级页面内容中获取有用信息
    def get_details(self, response):
        cur_url = response.url
        ntype = 0
        data = self.dba.get_empty_obj()

        if re.search(r'leadtc=ngen_tab-top_info', cur_url):
            ntype = 5
        elif re.search(r'n_ichiran_cst_n4_ttl', cur_url):
            ntype = 4
        elif re.search(r'n_ichiran_cst_n3_ttl', cur_url):
            ntype = 3
        elif re.search(r'n_ichiran_cst_n2_ttl', cur_url):
            ntype = 2
        elif re.search(r'n_ichiran_cst_n1_ttl', cur_url):
            ntype = 1
        elif re.search(r'n_ichiran_cst_bt_ttl', cur_url):
            ntype = 't'

        if ntype == 5 or ntype == 4 or ntype == 3 or ntype == 2 or ntype == 1:
            self.handle_common(data, response, ntype)
        elif ntype == 't':
            self.handle_t(data, response)

        self.dba.insert(data)

    # 处理 type5-1 页面的内容
    def handle_common(self, data, response, ntype):
        limit_len = 7  # 取前7行，之后的数据放到desc中

        data['ntype'] = str(ntype)
        data['title'] = response.css('.rnn-offerInfoHeader__title::text').extract_first()
        table = response.css('.rnn-group.rnn-group--l.rnn-textM .rnn-detailTable')
        theads = table.css('th.rnn-col-2::text').extract()  # .re(r'[\s\S]+')  # 标题
        conts = table.css('td.rnn-col-10').re(r'<p>[\s\S]+</p>')  # 内容

        if len(conts) < limit_len:
            msg = '招聘信息表格数量不对，当前url：%s' % response.url
            self.write_log(msg)
            return print(msg)

        data['url'] = response.url
        # 招聘时间
        during = response.css('.rnn-inlineBlock.rnn-offerInfoHeader__date.rnn-textM::text').extract_first()
        data['during'] = during[5:]
        # 标签
        tags = response.css('.rnn-inlineList.rnn-offerInfoHeader__iconList span::text').extract()
        data['tags'] = ','.join(tags)
        # 公司
        company = response.css('.rnn-offerCompanyName::text').extract_first()
        data['company'] = company

        fields = [
            'content',  # 工作内容 - - 仕事の内容
            'claim',  # 任职要求 - - 求めている人材
            'addr',  # 工作地点 - - 勤務地
            'salary',  # 工资 - - 給与
            'worktime',  # 上班时间 - - 勤務時間
            'holiday',  # 休假信息 - - 休日・休暇
            'welfare',  # 福利 - - 待遇・福利厚生
            'desc'  # 其他字段放到备注中
        ]

        idx = 0
        desc_arr = []  # 除了默认7个字段之外的字段
        for cont in conts:
            if idx < limit_len:  # 默认7个字段
                key = fields[idx]
                data[key] = self.format_cont(cont)
            else:  # 额外的内容
                desc_arr.append(
                    '<div>{0}##{1}</div>'.format(re.sub(r'\s+', '', theads[idx]), self.format_cont(cont)))
            idx += 1
        data['desc'] = ''.join(desc_arr)

    # 处理 type6 页面的内容
    def handle_t(self, data, response):
        limit_len = 7  # 取前7行，之后的数据放到desc中

        data['title'] = response.css('.QWZ12-140-B.JsRqmtJobTypeName::text').extract_first()
        dls = response.css('.recruit_details.clr')
        dts = dls.css('dt').re(r'<dt[\s\S]+</dt>')  # 标题
        conts = dls.css('dd').re(r'<p>[\s\S]+</p>')  # 内容

        if len(conts) < limit_len:
            msg = '招聘信息表格数量不对，当前url：%s' % response.url
            self.write_log(msg)
            return print(msg)

        data['ntype'] = 't'
        data['url'] = response.url
        # 招聘时间
        # 标签
        # 公司
        data['company'] = response.css('.leftcol.agent_width h1 span::text').extract_first()

        fields = [
            'content',  # 工作内容 - - 仕事の内容
            'claim',  # 任职要求 - - 求めている人材
            'addr',  # 工作地点 - - 勤務地
            'worktime',  # 上班时间 - - 勤務時間
            'salary',  # 工资 - - 給与
            'welfare',  # 福利 - - 待遇・福利厚生
            'holiday',  # 休假信息 - - 休日・休暇
            'desc'  # 其他字段放到备注中
        ]

        idx = 0
        desc_arr = []  # 除了默认7个字段之外的字段
        for cont in conts:
            scont = self.format_cont_old(cont)
            if idx < limit_len:  # 默认7个字段
                key = fields[idx]
                data[key] = scont
            else:  # 额外的内容
                desc_arr.append(
                    '<div>{0}##<p>{1}</p></div>'.format(self.format_cont_old(dts[idx]), scont))
            idx += 1
        data['desc'] = ''.join(desc_arr)

    # 新内容格式化，type1-5
    def format_cont(self, cont):
        s1 = re.sub(r'(\s+)|(<p>)', '', cont)  # 去空格  # re.sub(r'</?\w+>', '', s3) # 去所有标签
        s2 = re.sub(r'</p>', '<br>', s1)  # 内部p结束标签替换成br
        s3 = re.sub(r'(<br/?>)+', '<br>', s2)  # 多个br合并 <br><br>
        s4 = re.sub(r"'", "''", s3)  # 单引号替换
        return s4

    # 老版内容格式化，type-t
    def format_cont_old(self, cont):
        s1 = re.sub(r'(</?dt[\w\d\s\"\'\-_=]{0,}>)|(\s+)|(</?span[\w\d\s\"\'\-_=]{0,}>)', '', cont)  # 去空格、dt、span标签
        s2 = re.sub(r'(<br/?>)+', '<br>', s1)  # 去连在一块的br <br><br>
        s3 = re.sub(r'(</p><p>)', '', s2)  # 将内部连接的p标签替换为br
        s4 = re.sub(r'(^<p>)|(</p>$)', '', s3)  # 去外层p
        return re.sub(r"'", "''", s4)

    def write_log(self, cont):
        fileName = './logs.txt'
        with open(fileName, "a+") as f:  # “a+”以追加的形式
            f.write(cont)
            f.write('\n')
            f.close()
