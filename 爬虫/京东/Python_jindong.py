from lxml import etree
import requests
import time
import re 
import json
import csv

#设置请求头
headers={
	'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
	'referer':'https://www.jd.com/',
	'origin':'https://www.jd.com/',
}

#获取页面链接,转为html字符串
def page_link(link):
	response=requests.get(url=link,headers=headers)
	text=response.text
	return text

#获取商品信息的url
def product_url(url):
	html=etree.HTML(page_link(url))
	# 分组
	lis=html.xpath("//ul[contains(@class,'gl-warp')]/li")
	for li in lis:
		#获取商品id
		product_id=li.xpath('./@data-sku')[0]
		#拼接url
		parse_url="https://item.jd.com/%s.html"%product_id
		product_detail(parse_url,product_id)
		product_image(product_id)
	
		
#获取每个页面商品图片的url
def product_image(product_id):
	#获取商品简介的url
	recommend_url="https://c.3.cn/recommend?callback=handleComboCallback&methods=accessories&p=103003&sku={}&cat=670%2C671%2C672".format(product_id)
	text=page_link(recommend_url)
	text=re.search('.*?imageUrl?(.*?)?jpg',text).group()
	text=text.split('imageUrl":"')[-1]
	image_url='http://img11.360buyimg.com//n0/'+text
	return image_url

#解析商品信息
def product_detail(url,product_id):
	html=etree.HTML(page_link(url))

	#商品名称
	product_title=html.xpath("//div[@class='sku-name']/text()")
	product_title="".join(product_title).strip()

	#获取商品价格流程
	#拼接价格url---该参数是在控制台中找到的,采取的是ajax技术
	price_url="https://p.3.cn/prices/mgets?skuIds=J_%s"%product_id
	price_data=(page_link(price_url))
	price_data=re.sub(r'\[|\]','',price_data)
	#将json格式转化为字典类型
	price_data=json.loads(price_data)
	#获取商品价格
	product_price=price_data['p']

	#获取评论数的流程
	#拼接评论数的url ---该参数实在控制台中找到的,采取的ajax技术
	comment_list=[]
	comment_url="https://club.jd.com/comment/productCommentSummaries.action?referenceIds=%s"%product_id
	comment_data=page_link(comment_url)
	comment_data=json.loads(comment_data)
	comment_data=comment_data['CommentsCount'][0]

	#获取总评论数
	comment_list.append({
		"Comment_count":comment_data['CommentCount'],
		"Goodcomment_count":comment_data['GoodCount'],
		"GoodRate":comment_data["GoodRate"]
		})

	#获取商品图片
	image=product_image(product_id)

	product_data={
		"product_name":product_title,
		'product_price':product_price,
		"product_image":image,
		'product_comment':comment_list
	}
	data_storage(product_data)


#以json、csv文件存储数据
def data_storage(product_data):
	# 将数据存储在json文件中
	# with open("jingdong.json",'a',encoding="utf-8") as fp:
	# 	json.dump(product_data,fp,ensure_ascii=False)

	#将数据存储在csv文件中
	headers=['product_name','product_price','product_image','product_comment']
	values=[
		{'product_name':product_data['product_name'],
		"product_price":product_data['product_price'],
		"product_image":product_data['product_image'],
		"product_comment":product_data['product_comment']}
	]
	with open("jingdong.csv",'a',encoding="utf-8",newline='') as fp:
		writer=csv.DictWriter(fp,headers)
		writer.writeheader()
		writer.writerows(values)


def main():
	#爬取三十页的信息
	start_url=['https://search.jd.com/Search?keyword=%E7%AC%94%E8%AE%B0%E6%9C%AC&wq=%E7%AC%94%E8%AE%B0%E6%9C%AC&page={}&s=51&click=0'.format(i) for i in range(1,30)]
	for start_url in start_url:
		product_url(start_url)
		print("*"*30)
	
if __name__ == '__main__':
	main()