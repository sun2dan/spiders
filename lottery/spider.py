from scrapy import cmdline
import re, time


# 数据爬取入口
cmdline.execute("scrapy crawl two_color_ball".split())
