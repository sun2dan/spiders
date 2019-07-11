from scrapy import cmdline
import re, time


# 数据爬取入口
cmdline.execute("scrapy crawl tenshoku".split())
#cmdline.execute("scrapy crawl rikunabi".split())
