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
from MySQLdb.constants.FIELD_TYPE import NULL


proxies = {
	"http":""
		}

proxies_server = ["","http://221.176.14.72:80","http://111.1.36.6:80","http://113.225.37.43:80","http://202.108.23.247:80","http://111.12.251.162:80"]

logging.basicConfig(filename='/my-work/code/new_WebHandler/log.log',level=logging.INFO)


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
		self.extraInfo = []
		
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
		bWrite = True
		if self.link and self.index == TITLE+2:
			contentList.append('Downloader')
			contentList[-1]=ContentHandler(self.link)
			try:
				self.extraInfo= contentList[-1].run(self.link)
			finally:
				self.link=''
		if tag == "div" and len(self.inputFlow)>0:
			if len(self.extraInfo) == 2:
				self.inputFlow.append(self.extraInfo[0])
				self.inputFlow.append(self.extraInfo[1])
			for item in self.inputFlow:
				if '#1' in item:
					bWrite = False
			if bWrite:
				writer = csv.writer(self.f)
				writer.writerow(self.inputFlow)
			del self.inputFlow[:]
			del self.extraInfo[:]
			self.index = False
			logging.info('p-%s Done...' %self.page)
			
	def handle_data(self, rawdata):
		if self.index:
			data = rawdata.strip()
			data = data.translate(None,'\t\n')
			if len(data) != 0:
				if self.index == TITLE:
					id = re.search('\d+',self.link)
					if id:
						self.inputFlow.append(id.group())
						print 'ID : ' + id.group()
					else:
						self.inputFlow.append(' ')
						print 'ID : '
					self.inputFlow.append(data)
					print 'Name : '+data
					logging.info('p-%s is handling %s' %(self.page, data))
					print ('p-%s is handling %s' %(self.page, data))
					self.propertyName = data
				elif self.index == TITLE+1: 
					type = re.search('\d+',data)
					if not type:
						type = re.search('freehold',data,re.I)
					if type:
						print 'Type : '+type.group()
						self.inputFlow.append(type.group())
				elif self.index == TITLE+2:
					price = data.split("\r")[0].strip()
					price = price.translate(None,'\t\n, ')
					aera = data.split("\r")[-1].strip()
					aera = aera.translate(None,'\t\n, /')
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
			logging.info('	The referred content have downloaded')
			print('	The referred content have downloaded')
			self.dirPrefix = ''
						
	def run(self,link):
		resp = getRightWebResponse(self.URL,'<!-- Retrieve Media-->')
		if resp == NULL:
			return NULL
		Data = resp.content[resp.content.index('<!-- Retrieve Media-->'):]
		extraInfo = getTopNMrtInfo(Data)
		if self.dirPrefix == '':
			return extraInfo
		
		logging.info('Going to downloading data from %s' %link[link.rindex('/'):])
		print ('Going to downloading data from %s' %link[link.rindex('/'):])
		starttime = time.time()
		parser = SingleWebParser(self.dirPrefix)
		f  = open('/my-work/code/new_WebHandler/output_single_link.txt','wb')
		print >> f,Data 
		if Data:
			try:
				parser.feed(Data)
			except:
				pass
		
		logging.info('Time Spend on '+__name__+' : ------->'+str(time.time()-starttime))
		print('Time Spend on '+__name__+' : ------->'+str(time.time()-starttime))
		return extraInfo
			
			
def getCurrentTimeStr():
		return time.strftime("%Y%m%d")
	
	
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
	return NULL
	
def getTopNMrtInfo(Data):
	logging.info('	trying to collect TOP and MRT Information')
	print('	trying to collect TOP and MRT Information')
	infoList =[]
	topRoughInfo = re.search('top year.+\d+', Data,re.I).group()
	topYear = re.findall('\d+',topRoughInfo)
	if topYear:
		infoList.append(topYear[-1])
	mrtRoughInfo = re.search('(/.+mrt-station.+km\\))', Data,re.I).group()
	mrtDistance = re.search('\d+\.\d+',mrtRoughInfo)
	mrtName = re.search('[\w\s]+.mrt station',mrtRoughInfo,re.I)
	if mrtDistance and mrtName:
		mrtInfo = mrtDistance.group()+'-'+mrtName.group()
		infoList.append(mrtInfo)
	return infoList
