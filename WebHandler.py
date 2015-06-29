#!/usr/bin/python


import sys
import multiprocessing
import os
import datetime
import time
import logging
from DataHandler import MyHTMLParser
from DataHandler import proxies,proxies_server,getRightWebResponse


logging.basicConfig(filename='./log.log',level=logging.INFO)

url = 'http://www.propertyguru.com.sg/singapore-property-listing/property-for-sale/'
header = {'User-Agent':'Mozilla/4.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.1.2125.104 Safari/537.36'} 
payload = {'search_type':'district','property_type':'N','property_type_code[]':'CONDO[]','property_type_code[]':'APT','property_type_code[]':'EXCON',\
		'school':'','mrt':'','address':'','property_id':'','distance':'0.5','latitude':'','longitude':'','interest':'','hdb_type_group':'','minprice':'','maxprice':'900000','minbed':'2',\
		'maxbed':'','minsize':'500','maxsize':'','minsize_land':'','maxsize_land':'','freetext':'','minpsf':'','maxpsf':'','listing_posted':'','mintop':'1991','maxtop':'2015','sort':'date',\
		'order':'date','min_latitude':'','max_latitude':'','min_longitude':'','max_longitude':'','submit':''}
link = '?listing_type=sale&search_type=location&property_type=N&property_type_code[]=CONDO&property_type_code[]=APT&property_type_code[]=EXCON&school=&mrt=&address=&property_id=&distance=0.5&latitude=&longitude=&interest=&hdb_type_group=&minprice=&maxprice=900000&minbed=2&maxbed=&minsize=500&maxsize=&minsize_land=&maxsize_land=&freetext=&minpsf=&maxpsf=&listing_posted=&mintop=1991&maxtop=2015&sort=date&order=desc&min_latitude=&max_latitude=&min_longitude=&max_longitude=&submit='
TITLE = 1
SIZE  = 2

class DataHandler (multiprocessing.Process):
	def __init__(self,page):
		#multiprocessing.Process.__init__(self)
		self.page = page
		self.ST_time = datetime.time
		print 'p-%s (%s) is triggered...' % (page,os.getpid())
		logging.info('p-%s (%d) is triggered...' %(page,os.getpid()))
						
	def run(self):
		starttime = time.time()
		filename = 'List_'+time.strftime("%Y%m%d%H%M")+'.csv'
		f = open(filename,'a')
		hp=MyHTMLParser(self.page,f)	
		response = getRightWebResponse(url+str(self.page)+link, 'listing_item')			
		f  = open('output_'+str(self.page)+'.txt','wb')
		content = response.content[response.content.index("Normal List"):response.content.rindex("end: Normal List")]
		print >> f,response.content 

		TBD = hp.feed(content)
	
		logging.info('Time Spend on '+__name__+' : ------->'+str(time.time()-starttime))
		print('Time Spend on '+__name__+' : ------->'+str(time.time()-starttime))
		hp.close()
		f.close()
		
		
				
				

def main(argv):
	processList = list()
	print "\nGoing to query Perporty Guru by the following parameters: "
	print payload
	for key,val in payload.items():
		print key + ": "+val.rjust(20)
	for page in range(1,2):
		processList.append('p-'+str(page))
		processList[-1]=DataHandler(page)
		processList[-1].run()
		
	exit()
	


if __name__ == '__main__':
	main(sys.argv)

