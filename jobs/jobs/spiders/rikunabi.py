import scrapy
import math

class mingyan(scrapy.Spider):  # 继承scrapy.Spider类

    name = "rikunabi"  # 蜘蛛名
    page_size = 50  # 每页50条记录
    url_tpl = 'https://next.rikunabi.com/rnc/docs/cp_s00700.jsp?jb_type_long_cd=0500000000&jb_type_long_cd=1200000000&curnum='
    index = 0

    def start_requests(self):
        yield scrapy.Request(self.url_tpl + '1', callback=self.get_sum)
        # url = 'http://lab.scrapyd.cn/'
        # tag = getattr(self, 'tag', None)  # 获取tag值，也就是爬取时传过来的参数
        # if tag is not None:  # 判断是否存在tag，若存在，重新构造url
        #     url = url + 'tag/' + tag  # 构造url若tag=爱情，url= "http://lab.scrapyd.cn/tag/爱情"
        # yield scrapy.Request(url, self.parse)  # 发送请求爬取参数内容

    # 获取总记录数，计算出总页数，并打开第一页的中的50条详情记录、循环获取2-count页中的数据
    def get_sum(self, response):
        count = response.css('.rnn-pageNumber.rnn-textLl::text').extract_first()
        page_count = math.ceil(int(count) / self.page_size)
        for n in range(1, page_count):
            no = str(self.page_size * n + 1)
            res_url = self.url_tpl + no
            print(no)
            yield scrapy.Request(url=res_url, callback=self.get_list)
        self.get_list(response)  # 方法中的第一个参数 self 是默认的

    # 获取一级页面，包含分页数据的列表页面
    def get_list(self, response):
        detail_urls = response.css('.rnn-textLl.js-abScreen__title a::attr(href)').extract()
        for url in detail_urls:  # 循环获取每一条名言里面的：名言内容、作者、标签
            detail_url = response.urljoin(url)
            # yield scrapy.Request(url, self.parse_details)  # 发送请求爬取参数内容
            self.index += 1
            print(self.index, detail_url)

    def get_details(self, response):
        tags = response.css('.tags .tag::text').extract()  # 提取标签
        tags = ','.join(tags)  # 数组转换为字符串

        """
        """
        fileName = '%s.txt' % tags

        with open(fileName, "a+") as f:  # “a+”以追加的形式
            f.write('标签：' + tags)
            f.write('\n-------\n')
            f.close()
        pass
