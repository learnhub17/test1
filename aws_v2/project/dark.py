import web
import os
import json
import time
import urllib
from subprocess import call

urls = (
    '/venom', 'market',
    '/carnage', 'rss'
)

app = web.application(urls, globals())

class market:        
	def GET(self):
		query = urllib.parse.unquote(web.ctx.query)
		js = json.loads(query[1:])
		print (js)
		with open('market_query', 'w') as f:
			json.dump(js, f)

		tic = time.time()
		call(['python', 'venom.py'])

		JSON = ""
		dirs = os.listdir('crawl_data')
		for dir_name in dirs:
			if os.path.getmtime('crawl_data/' + dir_name)>=tic and "CRAWLEDY" in dir_name:
				with open("crawl_data/"+dir_name, 'r') as f:
					JSON = JSON + f.read()

		return ("[" + JSON[:-1] + "]")

class rss:        
	def GET(self):
		query = urllib.parse.unquote(web.ctx.query)
		js = json.loads(query[1:])
		with open('rss_query', 'w') as f:
			json.dump(js, f)

		os.system('python carnage.py')

		JSON = ""
		dirs = os.listdir('rss_data')
		for dir_name in dirs:
			with open("rss_data/"+dir_name, 'r') as f:
				JSON = JSON + f.read()

		# for url in js['urls']:
			# filename = url[:-1].split("/")[2:]
			# filename = "_".join(filename)
			# file = os.path.join(os.getcwd(), 'rss_data', 'CRAWLEDY-' +filename+ '.txt')

			# with open(file, 'r') as f:
			# 	JSON = JSON + f.read()
		
		return ("[" + JSON[:-1] + "]")

if __name__ == "__main__":
	app.run()