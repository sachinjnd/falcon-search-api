import falcon 
import json
import re
from selenium import webdriver
from wsgiref import simple_server


class SmartAnalyze:
	def on_get(self, req, resp):
		query = req.get_param('q')
		if not query:
			resp.status = falcon.HTTP_400
			resp.body = json.dumps({ 'status': 'INVALID_REQUEST' })
			return

		resp.status = falcon.HTTP_200
		GoogleSearch.driver = webdriver.PhantomJS()
		googleSearch = GoogleSearch(query)
		output = googleSearch.getResult()
		GoogleSearch.driver.quit()
		if not output:
			resp.body = json.dumps({ 'status': 'FAILED' })
			return

		imdbId = mineImdbId(output)
		if not imdbId:
			resp.body = json.dumps({ 'status': 'FAILED' })
			return

		result = { 'status': 'SUCCESS', 'i': imdbId }
		resp.body = json.dumps(result)
		return


class GoogleSearch:
	"""docstring for GoogleSearch"""
	driver = None
	googleUrl = 'http://www.google.co.in/search?num=1&q='
	xpath = '//*[@id="ires"]/ol/div/h3/a'

	def __init__(self, query):
		#super(GoogleSearch, self).__init__()
		self.query = query.strip() + ' imdb'
		#print 'Created'

	def getResult(self):
		GoogleSearch.driver.get(GoogleSearch.googleUrl + self.query)
		elements = GoogleSearch.driver.find_elements_by_xpath(GoogleSearch.xpath)
		for element in elements:
			return element.get_attribute('href')
		return None
		

def mineImdbId(s):
	m = re.search(r'www\.imdb\.com\/title\/([^\n]+)\/', s)
	if m:
		return m.group(1)
	return None

 
app = falcon.API()
smartAnalyze = SmartAnalyze()
app.add_route('/analyze', smartAnalyze)


if __name__ == '__main__':
	httpd = simple_server.make_server('127.0.0.1', 8000, app)
	httpd.serve_forever()



