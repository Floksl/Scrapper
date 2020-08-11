# install xlsxwriter, requests, BeautifulSoup4

import xlsxwriter
import requests
import time
from datetime import date
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# webside friendly retry 
def requests_retry_session(
	retries=3,
	backoff_factor=0.3,
	status_forcelist=(500, 502, 504),
	session=None,
	):
		session = session or requests.Session()
		retry = Retry(
			total=retries,
			read=retries,
			connect=retries,
			backoff_factor=backoff_factor,
			status_forcelist=status_forcelist,
		)
		adapter = HTTPAdapter(max_retries=retry)
		session.mount('http://', adapter)
		session.mount('https://', adapter)
		return session

def get_html(get_url):
	t0 = time.time()
	try:
		response = requests_retry_session().get(get_url , timeout = 5)
	except Exception as x:
		print('It failed :(', x.__class__.__name__)
	else:
		print('It eventually worked', response.status_code)
	finally:
		t1 = time.time()
		print('Took', t1 - t0, 'seconds')
		return response


def getxlsx(name):
	datum = date.today()
	workbook = xlsxwriter.Workbook(name + datum.strftime("-%d-%m") + '.xlsx') 
	sheet1 = workbook.add_worksheet()
	return workbook, sheet1

def header(sheet):
	write = ["HTTP", "NAZIV DEL. MESTA", "OPIS", "Datum", "Podjetje", "Kraj"]
	for numb, word in enumerate(write):
		sheet.write(0,numb, word)	

def getlastpage():
	response = get_html(url)
	if response is not None:
		soup = BeautifulSoup(response.text, "html.parser")
		number = soup.find("li", class_="PagedList-skipToLast")
		return int(number.text)

''' search is [y position, and split '<h2 class="title">'],
	"detail" has many data that we increment
	looking at "p" you can get class or no class
	!!!MIGHT BE IMPROVED?!!!'''
def writedata(write_here, link, x):
	search = [[1 ,"h2", {"class" : "title"}],[2, "p", {}],[3, "div", {"class" : "detail"}]]	
	for y, data, claz in search:
		for result in link.find_all(data, claz):
			write_here.write(x, y, result.text)
			y += 1


def išči_mojedelo():
	start = time.time()
	x = 1
	wb, sheet1 = getxlsx("Moje_Delo")
	header(sheet1)

	for page in range(1, getlastpage() + 1):
		print("fetching page {}".format(page))
		response = get_html(url + str(page))

		if response is not None:
			soup = BeautifulSoup(response.text, 'html.parser')
			for link in soup.find_all('a', class_="w-inline-block job-ad deluxe w-clearfix", href=True):
				sheet1.write(x, 0, "https://www.mojedelo.com"+ link['href'])
				writedata(sheet1, link, x)
				x+= 1
			
			for link in soup.find_all('div', class_="w-inline-block job-ad top w-clearfix"):
				for href in link.find_all('a',class_="details overlayOnHover1", href=True):
					sheet1.write(x, 0, "https://www.mojedelo.com"+ href['href'])
					writedata(sheet1, link, x)
				x+= 1

	wb.close()
	end = time.time()
	print(f"Total time: {(end - start)/60} minutes")

url = "https://www.mojedelo.com/prosta-delovna-mesta/vsa-podrocja/osrednjeslovenska?p="


išči_mojedelo()