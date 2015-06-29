#!/usr/bin/python


import requests
import sys
import csv
import multiprocessing
import os
import logging
import urllib
import time
import re
from HTMLParser import HTMLParser
from pango import AttrScale


proxies = {
	"http":""
		}

proxies_server = ["","http://120.194.216.169:80","http://183.207.229.11:80","http://120.198.243.79:80","http://221.238.197.34:80","http://183.207.229.11:26"]

logging.basicConfig(filename='./log.log',level=logging.INFO)


TITLE = 1
SIZE  = 2
WebPrefix = "http://www.propertyguru.com.sg/"
header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.1.2125.104 Safari/537.36'}



class MyHTMLParser(HTMLParser): 

	def __init__(self,page,f):   
		HTMLParser.__init__(self) 
		self.page = page  
		self.links = []   
		self.index = 0
		self.parNid2bClect = 0
		self.inputFlow = []
		self.propertyName = ''
		self.f = f
		self.link=''
		
	def handle_starttag(self, tag, attrs):   
	#print "Encountered the beginning of a %s tag" % tag
		if self.index and tag == "p":
			self.index += 1
		for tup in attrs:   
			if len(tup) == 2:
				item,value = tup
				if "bluelink" in value:
					self.index = TITLE
				if self.index == TITLE and "href" in item:	
					self.link = value
					
					
			
	def handle_endtag(self, tag):
		contentList = list()
		if self.link and self.index == TITLE+2:
			contentList.append('Downloader')
			contentList[-1]=ContentHandler(self.link)
			if contentList[-1].dirPrefix:
				logging.info('Going to downloading data from %s' %self.link[self.link.rindex('/'):])
				print ('Going to downloading data from %s' %self.link[self.link.rindex('/'):])
				try:
					contentList[-1].run()
				finally:
					self.link=''
		if tag == "div" and len(self.inputFlow)>0:
			writer = csv.writer(self.f)
			writer.writerow(self.inputFlow)
			del self.inputFlow[:]
			self.index = False
			logging.info('p-%s Done...' %self.page)
			
	def handle_data(self, rawdata):
		if self.index:
			data = rawdata.strip()
			data = data.translate(None,'\t\n')
			if len(data) != 0:
				if self.index == TITLE:
					self.inputFlow.append(data)
					print 'Name : '+data
					logging.info('p-%s is handling %s' %(self.page, data))
					print ('p-%s is handling %s' %(self.page, data))
					self.propertyName = data
				elif self.index == TITLE+1: 
					self.inputFlow.append(data)
					print 'Type : '+data
				elif self.index == TITLE+2:
					price = data.split("\r")[0].strip()
					price = price.translate(None,'\t\n S$')
					aera = data.split("\r")[-1].strip()
					aera = aera.translate(None,'\t\n /')
					self.inputFlow.append(price)
					print 'Price: '+price
					self.inputFlow.append(aera)
					print 'Aera: '+aera
				else:
					logging.info('++++++++++++++++++++++++++++++++++++\n')
					print('++++++++++++++++++++++++++++++++++++\n')
			

class SingleWebParser(HTMLParser):
	
	def __init__(self,dirPrefix):
		HTMLParser.__init__(self)
		self.dirPrefix = dirPrefix
		self.b_data = False		
		
	def handle_starttag(self, tag, attrs):
		if tag == 'script':
			for tup in attrs:
				if len(tup) == 2:
					item, value = tup
					if item == 'type' and value == 'text/javascript':
						self.b_data = True
			
		
	def handle_endtag(self, tag):
		pass
		
	def handle_data(self, data):
		i = 1
		if self.b_data and 'addMediaItem' in data:
			data = data[data.index('addMediaItem')+len('addMediaitem'):data.rindex('addMediaItem')]
			logging.info("downloading img...")
			data = re.sub('[\r\n\s]','',data)
			linkList = re.findall('http\S{30,100}\.jpg',data)
			for link in linkList:
				try:
					urllib.urlretrieve(link,self.dirPrefix+str(i)+'.jpg')
				except:
					logging.info('	'+self.dirPrefix+' '+str(i)+' of '+str(len(linkList))+ '---->  failed')
					print('	'+self.dirPrefix+' '+str(i)+' of '+str(len(linkList))+ ' ---->  failed')
					pass
				finally:
					logging.info('	'+self.dirPrefix+' '+str(i)+' of '+str(len(linkList))+ '---->  downloaded')
					print('	'+self.dirPrefix+' '+str(i)+' of '+str(len(linkList))+ ' ---->  downloaded')
					urllib.urlcleanup()
					i+=1
					time.sleep(1)
		self.b_data=False
				
		
class ContentHandler (multiprocessing.Process):
	def __init__(self,URL):
		#multiprocessing.Process.__init__(self)
		logging.info('    subprocess triggered to process '+URL)
		self.URL = WebPrefix+URL
		
		self.dirPrefix ='/my-work/data/'+URL[URL.index('/',3)+1:].replace('/','_')+'/'
		if not os.path.exists(self.dirPrefix):
			os.system('mkdir -p '+self.dirPrefix)
		else:
			logging.info('	The referred content have downloaded, exiting download process..')
			logging.info('	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
			print('	The referred content have downloaded, exiting download process..')
			print('	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
			self.dirPrefix = ''
						
	def run(self):
		time.sleep(5)
		starttime = time.time()
		parser = SingleWebParser(self.dirPrefix)
		resp = getRightWebResponse(self.URL,'<!-- Retrieve Media-->')
		Data = resp.content[resp.content.index('<!-- Retrieve Media-->'):]
		if Data:
			try:
				parser.feed(Data)
			except:
				pass
		
		logging.info('Time Spend on '+__name__+' : ------->'+str(time.time()-starttime))
		print('Time Spend on '+__name__+' : ------->'+str(time.time()-starttime))
			
			
def getCurrentTimeStr():
		return time.strftime("%Y%m%d%H%M")
	
	
def getRightWebResponse(url,targetStr):
	s = requests.session()
	for ipSocket in proxies_server:
		proxies['http']= ipSocket
		try:
			if ipSocket:
				print('	trying from Proxy : '+ ipSocket)
				response = s.get(url, headers = header,proxies = proxies)
			else:
				print('	trying from local machine')
				response = s.get(url, headers = header)
		except:
			pass
		if targetStr in response.content:
			print "	Request Accpted"
			logging.info('Request Accpted')
			return response
		else:
			logging.info(response.content)
			
			
	print "\nOh,no! No data retreived, exiting.."
	logging.info('Request Rejected by Website')
	exit()
