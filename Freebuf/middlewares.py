# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display    # linux only


class SeleniumMiddleware():
    def __init__(self):
        self.display = Display(visible=0, size=(800, 800)) # linux only
        self.display.start() # linux only
        option = webdriver.ChromeOptions()
        option.add_argument('headless')  # 不显示窗口
        option.add_argument('--no-sandbox')  # linux root user only
        prefs = {
            'profile.default_content_setting_values': {  # 无图模式
                'images': 2
            }
        }
        option.add_experimental_option('prefs', prefs)
        self.browser = webdriver.Chrome(chrome_options=option)
        self.browser.set_page_load_timeout(10)

    def __del__(self):
        self.browser.quit()
        self.display.stop()   #linux only

    def process_request(self, request, spider):
        try:
            self.browser.get(request.url)
        except TimeoutException:
            print('超时')
            self.browser.execute_script('window.stop()')
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'div')))    #等待js执行结束并跳转到真正的首页
        return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                            status=200)

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.browser.quit, signal=signals.spider_closed)
        return s

