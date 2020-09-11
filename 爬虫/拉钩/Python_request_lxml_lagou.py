# ---------------------传统requests、lxml爬取拉钩网站的信息------------

from lxml import etree
import requests
import time

# 设置请求头
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
	'Referer':'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
	'Host':'www.lagou.com',
	'origin':'https://www.lagou.com',
	'Connection':'close',
	# X-反爬虫----
	# accept-Encoding:gzip--->加速访问
	'X-Anit-Forge-Code':'0',
	'X-Anit-Forge-Token':'None',
	'X-Requested-With':'XMLHttpRequest',
	'Accept-Encoding':'gzip'}

# 创建一个代理ipr
proxy={
'http':'114.101.252.240:23518'
}


# 获取职位信息url
def requests_list_page():
	start_url='https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput='
	parse_url='https://www.lagou.com/jobs/positionAjax.json?px=default&needAddtionalResult=false'
	
	# 设置post请求的一些参数
	data={
	'first':'true',
	'pn':1,
	'kd':'python'
	}

	# 创建一个session()
	session=requests.Session()
	# 请求start_url,获取搜索页面的cookies
	session.get(url=start_url,headers=headers,proxies=proxy)
	# 存储cookies
	cookie=session.cookies
	# 由于拉勾使用的是ajax异步加载，所以要手动更改data
	for i in range(1,4):
		data['pn']=i
		# 再次访问parse_url
		response=session.post(url=parse_url,headers=headers,data=data,proxies=proxy,cookies=cookie)
		# json方法，如果返回的是json数据，那么这个方法会自动的load成字典
		result=response.json()
		# 获取positionId,得到各页面的url-->resul是一个列表
		positions=result['content']['positionResult']['result']
		for position in positions:
			positionId=position['positionId']
			position_url='https://www.lagou.com/jobs/%s.html?show=a8bc6f292c7a412f961a0f501d1c6f08'%positionId
			# 调用获取职位信息函数
			parse_position_detail(position_url)
			time.sleep(2)
			break
		break


# ------------requests、lxml爬取拉勾网的步骤-------------
# ------------1.获取单页公司的url
# ------------2.获取单个公司的职位信息的url
# ------------3.爬取，解析数据

# -----------------------注意事项-----------
# ------------1.请求头必须包含Referer、user-agent、cookie
# ------------2.创建session，获取cookie再访问url
# ------------3.得到网页源码之后，获取positionId才能真正得到职位信息的url
# ------------4.提倡使用代理，防止IP被封
# ------------5.拉勾网使用的是AJAX异步加载信息，所以如果要获取多页面的公司url
# ------------应手动修改data中的'pn'参数的值

# 获取职位信息
def parse_position_detail(url):
	response=requests.get(url=url,headers=headers,proxies=proxy)
	text=response.content.decode('utf-8')
	html=etree.HTML(text)
	position_all={}
	# 获取职位名
	position_names=html.xpath('//div[@class="job-name"]/h1/text()')
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
	# 将所有职位信息存储在position_all中
	print(position_all)
			
def main():
	requests_list_page()

if __name__ == '__main__':
	main()


