# ---------selenium、chromedriver爬取拉钩网页-------------

from lxml import etree
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class LagouSpider(object):
	driver_path=r'D:\chromedriver\chromedriver.exe'
	def __init__(self):
		# 设置浏览器驱动
		self.driver=webdriver.Chrome(
			executable_path=LagouSpider.driver_path)
		self.url='https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput='

# ------------分页设置，将单个页面源码传给parse_list_page()----------------
	# driver.page_source得到初始页面源码，传入给parse_list_page()，
	# 调用click()函数自动点击下一页
	def run(self):
		# 请求自动登录
		self.driver.get(self.url)
		# 定位给也不要按钮,自动点击
		first_btn=self.driver.find_element_by_xpath("//div[@class='body-btn']")
		first_btn.click()
		while True:
			# 获取网页源代码
			source=self.driver.page_source
			# 设置延时等待,在这时间段内一直若区数据，若没有则异常
			WebDriverWait(driver=self.driver,timeout=10).until(
				EC.presence_of_element_located((
					By.XPATH,'//div[@class="pager_container"]/span[last()]'))
				)
			# 调用方法parse_list_page()
			self.parse_list_page(source)
			# 定位下一页的按钮元素
			next_btn=self.driver.find_element_by_xpath(
				'//div[@class="pager_container"]/span[last()]')
			# get_attribute("class")--->返回元素next_btn的class属性值
			if "pager_next_disabled" in next_btn.get_attribute("class"):
				break
			else:
				# # 自动点击下一页按钮
				next_btn.click()
			time.sleep(1)

			
	# 获取单页所有公司职位信息的url
	def parse_list_page(self,source):
		html=etree.HTML(source)
		# 获取职位信息的链接
		links=html.xpath('//a[@class="position_link"]/@href')
		for i in  links:
			self.request_detail_page(i)
			time.sleep(1)

# -----------------------------67行细节注意------------------------------
	# 获取单个公司职位信息的源码,并且跳转到相应页面后再关闭
	def request_detail_page(self,url):
		# 用jsp打开一个新页面，这种方式会保留原页面
		self.driver.execute_script("window.open('%s')"%url)
		# 跳转到新打开的页面
		self.driver.switch_to.window(self.driver.window_handles[1])
		WebDriverWait(driver=self.driver,timeout=10).until(
			EC.presence_of_element_located((
				By.XPATH,'//div[@class="job-name"]/h1'))
			#//div[@class="job-name"]/h1/text()-->这里面的XPATH是找不到
			#文本信息的，因此要把text()去掉
			)
		# 获取网页源代码
		source=self.driver.page_source
		self.parse_detail_page(source)
		# 关闭当前页面
		self.driver.close()
		# 继续切换原职位列表页
		self.driver.switch_to.window(self.driver.window_handles[0])


	# 详细解析单个公司的职位信息
	def parse_detail_page(self,source):
		html=etree.HTML(source)
		position_all={}
		# 获取职位名
		position_names=html.xpath('//div[@class="job-name"]/h1/text()')[0].strip()
		position_all['position_names']=position_names
		# 获取职位标签
		position_Tags=html.xpath('//dd[@class="job_request"]/h3/span/text()')
		position_all['position_tags']=position_Tags
		# 获取职位诱惑
		position_advantages=html.xpath('//dd[@class="job-advantage"]/p/text()')
		position_all['position_advantages']=position_advantages
		# 获取职位描述   ------position_descrip
		position_descrip=[]
		position_descriptions_s=html.xpath('//div[@class="job-detail"]/p/text()')
		for i in position_descriptions_s:
			position_descriptions=i.strip()
			position_descrip.append(position_descriptions)	
		position_all['position_descrip']=position_descrip
		#获取职位地址   --------position_address
		position_address=[]
		position_addre=html.xpath('//div[@class="work_addr"]/a/text()')
		for i in position_addre:
			position_addres=i.strip()
			position_address.append(position_addres)
		position_all['position_address']=position_address
		# 获取公司名字
		position_company=html.xpath("//img[@class='b2']/@alt")
		position_all['company_name']=position_company
		# 将所有职位信息存储在position_all中
		print(position_all)
		print("---------分界线-------------")
		print("---------------------红色警告--------------")


if __name__ == '__main__':
	spider=LagouSpider()
	spider.run()