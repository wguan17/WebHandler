#!/usr/bin/python

import re
import os
import subprocess
import logging
import time
import csv

logging.basicConfig(filename = '/my-work/code/new_WebHandler/log.log',level = logging.INFO)


class dBHandler:
	def __init__(self,filename):
		self.loadConfig()
		self.filename = filename
		
	def loadConfig(self):
		with open('/my-work/code/new_WebHandler/postgres-inf.cfg','r') as config:
			for line in config:
				if line and not re.match('#',line):
					param = line.strip().split('=')
					if re.search('hostname',param[0],re.I):
						self.dbhost = param[1]
					elif re.search('user',param[0],re.I): 
						self.dbuser = param[1]
					elif re.search('passwd',param[0],re.I):
						self.passwd = param[1]
					elif re.search('port',param[0],re.I):
						self.dbport = param[1]
					elif re.search('database_name',param[0],re.I):
						self.dbname = param[1]
					elif re.search('db_table',param[0],re.I):
						self.dbtable = param[1]
				
	
	def creatNConnectNamePipe(self):
		sqloutfile = "/my-work/code/new_WebHandler/tmp.csv"
		logfile = "/my-work/code/new_WebHandler/dlp_log.log"
		if os.path.exists(sqloutfile):
			os.unlink(sqloutfile)
		os.mkfifo(sqloutfile)
		aproc = subprocess.Popen(["/usr/local/infobright-products/dlp/dataprocessor",
						 "--server", "postgres", "-H", self.dbhost, "-P", self.dbport,
						 "-L", self.dbuser, "-D", self.dbname, "-T", self.dbtable,
						 "-I", "pipe", "-i", sqloutfile, "-f", "txt_variable",
						 "-X", "-l", logfile])
		
		return sqloutfile
	
	def loadDataviaCsv(self,sqloutfile,queryoutfile,selectfile,logfile):
		insertdata = []
		with open(queryoutfile,'r') as sourcefile:
			with open(sqloutfile,'w') as destfile:
				writer = csv.writer(destfile)
				for line in sourcefile:
					line = re.sub('[\r\n\s"]','',line)
					price = re.search('s\$\d+',line,re.I)
					if not price:
						continue
					id = re.match('\d+',line)
					if id:
						selectCmd = 'select listno,udtmnprice from properties where listno = {0};'.format(id.group(0))
						psqlCmd = "psql -d{0} -U{1} -h{2} -p{3} -A -F, -q -c\"{5}\" ".\
						format(self.dbname, self.dbuser, self.dbhost, self.dbport, selectfile, selectCmd)
						args = [psqlCmd]
						aproc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
						stdout, stderr = aproc.communicate()
						if stdout:
							logging.info(stdout)
							records = stdout.split("\n")
							lastPrice = re.findall('\d+\-S\$\d+',records[1],re.I)
							if lastPrice:
								selectPrice = lastPrice[-1].split("-")
								if price.group()==selectPrice[-1]:
									pass
								else:
									uptmnpriceCol=getCurrentTimeStr()+"-"+price.group(0)+"|"+records[1].split(",")[1]
									insertdata = line.split(",")
									insertdata.pop(3)
									insertdata.insert(4,uptmnpriceCol)
									writer.writerow(insertdata)
							else:
								uptmnpriceCol=getCurrentTimeStr()+"-"+price.group(0)
								insertdata = line.split(",")
								if len(insertdata) == 7:
									insertdata.pop(3)
									insertdata.insert(4,uptmnpriceCol)
									writer.writerow(insertdata)
															
						if stderr:
							logging.error(stderr)
							
					del insertdata[:]
					
		dlpcmd = "/usr/local/infobright-products/dlp/dataprocessor --server postgres -H{0} -P{1} -L{2} -D{3} -T{4} -i{5} -ftxt_variable --fields-terminated-by=',' -X -l{6}".\
			format(self.dbhost, self.dbport, self.dbuser, self.dbname, self.dbtable, sqloutfile, logfile)
		dlpargs = [dlpcmd]
		aproc = subprocess.Popen(dlpargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		stdout, stderr = aproc.communicate()
		if stdout:
			logging.info(stdout)
		if stderr:
			logging.error(stderr)
		else :
			os.unlink(queryoutfile)
		
	
	def run(self):
		
		sqloutfile = "/my-work/code/new_WebHandler/tmp.csv"
		queryoutfile = self.filename
		selectfile = '/my-work/code/new_WebHandler/selectFile.csv'
		logfile = "/my-work/code/new_WebHandler/dlp_log.log"
		try:
			self.loadDataviaCsv(sqloutfile, queryoutfile, selectfile, logfile)
		finally:
			os.unlink(sqloutfile)
		
					
	
def getCurrentTimeStr():
		return time.strftime("%Y%m%d")
				
		
	
	
if __name__=='__main__':
	test=dBHandler('List_20150722.csv')
	test.run()