# -*- coding: utf-8 -*-
import re
import time,sys
from selenium import webdriver
from bs4 import BeautifulSoup
#extract the set of users in a given html page and add them to the given set
fw =  open('result.txt','w')
reviewtext_list=list()
rating_list=list()
date_list=list()
url_list=list()
link_list=list()
page = 1
review_num = 0

def getReview(html):
	soup = BeautifulSoup(html, 'html.parser')
	reviewcontainer_divs = soup.findAll("div",{"class":"BVRRReviewTextContainer"})
	for reviewcontainer_div in reviewcontainer_divs:
		soup = BeautifulSoup(`reviewcontainer_div`, 'html.parser')
		reviewtext_divs = soup.findAll("span",{"class":"BVRRReviewText"})
		temp = ""
		for reviewtext_div in reviewtext_divs:
			temp += reviewtext_div.text
		reviewtext_list.append(temp)

def getRating(html):
	soup = BeautifulSoup(html, 'html.parser')
	rating_divs = soup.findAll("div",{"id":"BVRRRatingOverall_Review_Display"})
	for rating_div in rating_divs:
		ratings = re.finditer('<span class="BVRRNumber BVRRRatingNumber" property="v:value">(.*?)</span>',`rating_div`)
		for rating in ratings:
			rating_list.append(rating.group(1).strip())

def getDate(html):
	review_dates = re.finditer('<span property="v:dtreviewed" content="(.*?)" class="BVRRValue BVRRReviewDate">',html)
	for review_date in review_dates:
		date_list.append(review_date.group(1).strip())

def getItemList(html):
	itemlist = re.finditer('<div class="sku-title" itemprop="name"><h4><a href="(.*?)" data-rank="pdp">',html)
	for item in itemlist:
		link_list.append("http://www.bestbuy.com"+item.group(1).strip())

def writeFile():
	try:
		for i in range(len(reviewtext_list)):
			global review_num
			fw.write('www.bestbuy.com - '+`review_num`+'\n'+reviewtext_list[i].encode('utf-8')+'\n'+rating_list[i]+'\n'+date_list[i]+'\n\n') 
			review_num+=1
		del reviewtext_list[:]
		del rating_list[:]
		del date_list[:]
	except Exception, e:
		print e

def parsePage(html):
	global review_num
	getReview(html)
	getRating(html)
	getDate(html)
	#write to file
	writeFile()
	print 'page',page,'done'



#main url of the item
url='http://www.bestbuy.com/site/searchpage.jsp?st=samsung+tv&_dyncharset=UTF-8&id=pcat17071&type=page&sc=Global&cp=1&nrp=15&sp=&qp=&list=n&iht=y&usc=All+Categories&ks=960&keys=keys'

#open the browser and visit the url
driver = webdriver.Chrome('./chromedriver')
driver.get(url)

#sleep for 2 seconds
time.sleep(2)

#get the page url list
getItemList(driver.page_source)

for link in link_list:
	page = 1
	print "Scraping:\n"+link
	driver.get(link)
	#find the 'Ratings and Reviews' button based on its css path
	button=driver.find_element_by_css_selector('#ui-id-3')
	button.click() #click on the button
	time.sleep(2) #sleep
	#parse the first page
	if review_num >=10:
		break
	parsePage(driver.page_source)
	
	

	page=2
	while review_num<10:
	    #get the css path of the 'next' button
	    cssPath='#BVRRDisplayContentFooterID > div > span.BVRRPageLink.BVRRNextPage > a'
	    
	    try:
	        button=driver.find_element_by_css_selector(cssPath)
	    except:
	        error_type, error_obj, error_info = sys.exc_info()
	        print 'STOPPING - COULD NOT FIND THE LINK TO PAGE: ', page
	        print error_type, 'Line:', error_info.tb_lineno
	        break

	    #click the button to go the next page, then sleep    
	    button.click()
	    time.sleep(2)
	    
	    #parse the page
	    parsePage(driver.page_source)
	    
	    page+=1
	    
fw.close()



