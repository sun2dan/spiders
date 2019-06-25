import scrapy
import math, re, os, sys

path = os.getcwd()
print(path)
sys.path.append(path+'/jobs/spiders/')
from dba import DBA

class JobOperator(scrapy.Spider):  # 继承scrapy.Spider类
    debug = True
    name = "rikunabi"  # 蜘蛛名
    page_size = 50  # 每页50条记录
    url_tpl = 'https://next.rikunabi.com/rnc/docs/cp_s00700.jsp?jb_type_long_cd=0500000000&jb_type_long_cd=1200000000&curnum=1'
    index = 0
    dba = DBA()

    def start_requests(self):
        yield scrapy.Request(self.url_tpl, callback=self.get_sum)

    # 获取总记录数，计算出总页数，并打开第一页的中的50条详情记录、循环获取2-count页中的数据
    def get_sum(self, response):
        count = response.css('.rnn-pageNumber.rnn-textLl::text').extract_first()
        page_count = math.ceil(int(count) / self.page_size)

        for n in range(0, page_count):
            if self.debug and n > 0: break  # debug 时只取第一页
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

        if len(detail_urls) != 50 or len(ntypes) != 50:
            return print('url和ntype不匹配，长度分别为：', len(detail_urls), len(ntypes))

        for url in detail_urls:
            if self.debug and idx > 0:
                break
            ntype = ntypes[idx]

            detail_url = response.urljoin(url)
            if ntype == '5':
                detail_url = re.sub(r'\/nx1_', r'/nx2_', detail_url)
                detail_url = re.sub(r'\?[\s\S]+$', r'?leadtc=ngen_tab-top_info', detail_url)
                # res: https://next.rikunabi.com/company/cmi0520246015/nx2_rq0017615082/?leadtc=ngen_tab-top_info
            elif ntype == '4' or ntype == '3' or ntype == '2' or ntype == '1':
                pass
            elif ntype == 't':
                pass
            else:
                pass

            idx += 1
            self.index += 1
            print(self.index, detail_url)

            # 请求二级页面
            yield scrapy.Request(detail_url, self.get_details)  # 发送请求爬取参数内容

    # 从二级页面内容中获取有用信息
    def get_details(self, response):
        idx = 0
        cur_url = response.url
        ntype = 0
        data = self.dba.get_empty_obj()

        if re.search(r'\/nx2_', cur_url): ntype = 5

        if ntype == 5:
            data['title'] = response.css('.rnn-offerInfoHeader__title::text').extract_first()
            table = response.css('.rnn-group.rnn-group--l.rnn-textM .rnn-detailTable')
            conts = table.css('td.rnn-col-10')
            # data['content'] = conts[0]
            # for cont in conts:
            #     data[]
            print(len(conts), conts)

        self.dba.insert(data)
        # fileName = '%s.txt' % idx
        # with open(fileName, "a+") as f:  # “a+”以追加的形式
        #     f.write(title)
        #     f.write('\n-------\n')
        #     f.close()
        pass
