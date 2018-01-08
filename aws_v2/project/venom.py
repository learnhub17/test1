import datetime
import time
import json
import os
import re

import scrapy
from scrapy.crawler import CrawlerRunner  
from scrapy.http import HtmlResponse
from twisted.internet import reactor

from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup

class Venom(scrapy.Spider):
    
    name = 'venom'
    proxy = {'proxy': ":8118"}  # {'proxy': "http://:8118"}

    def start_requests(self):

        print (self.name)
        print (self.allowed_domains)

        for field in self.fields:
            url = field['url']
            if url.startswith('http'):  #if valid URL
                yield scrapy.Request(url=url, callback=self.login, meta=self.proxy)

    def login(self, response):
        ch = 0
        for i, field in enumerate(self.fields):
            if response.url == field['url']:
                if field['username'] and field['password']:
                    print ("***LOGIN***")
                    ch = 1                 
                    username = field['username']
                    password = field['password']
        # body = response.body.decode('utf-8').lower()
        # if "login" in body and "password" in body:
                    
        #     captcha = ""
        #     if "captcha" in body:
        #         print ("*****CAPTCHA*****")
        #         imgs = response.xpath('//img/@src').extract()
        #         for img in imgs:
        #             print (response.url +'/'+ img)
        #         print ("Enter CAPTCHA: ", end="")
        #         captcha = input()

                    return scrapy.FormRequest.from_response(response,
                        formdata={'username':username, 'password': password},
                        # formdata={'username':'birju', 'password':'birju@123', 'captcha':captcha},
                        callback=self.parse, meta=self.proxy)
            
        if ch==0: 
            return self.parse(response)

    def parse(self, response):
        
        print ("++++++++++++++++++++++++++++++++++", response, "+++++++++++++++++++++++++++++++++++++")
        url = response.url
        
        crawled.append(url)
        crawl_prefix.append(url.split('/')[2])
        webAll[url] = []
        webCrawl[url] = []

        if not os.path.exists("crawl_data"):
            os.mkdir("crawl_data")

        filename = url.split("/")[2:]
        filename = "_".join(filename)
        filename1 = os.path.join(os.getcwd(), 'crawl_data', 'CRAWLEDY-' +filename+ '.txt')
        filename2 = os.path.join(os.getcwd(), 'crawl_data', 'CRAWLEDX-' +filename+ '.txt')

        soup = BeautifulSoup(response.body, "html.parser")

        for script in soup.find_all('script'):
            script.extract()
        for style in soup.find_all('style'):
            style.extract()
        for form in soup.find_all('form'):
            form.extract()

        js = {}
        nc = 0
        wc = 0
        pc = 0

        title = soup.title.string
        js['crawl_name'] = self.name
        js['market'] = title
        js['url'] = url
        js['date'] = datetime.datetime.now()

        js['text'] = ""
        with open(filename2, 'w') as f2:
            for string in soup.stripped_strings:
                f2.write(string+"\n")
                js['text'] = js['text'] + string #+ "\n"

        # es.index(index=index, doc_type='page text', body=js)  # check if already indexed before
        js.pop("text")

        js['category'] = "Contraband"
        js['seller_name'] = "Dark Web People"
        js['shipping_country'] = "Unknown"
        js['product_desc'] = ""

        prev = ""
        weights = "[Gg]rams|GRAMS|[Gg]ram|GRAM|[Gg]r|[Gg]|m[Ll]|[Xx] [Pp]ills|[Xx]|[Oo]unces|[Oo]unce|[Oo][Zz]|[Hh]its|HITS|[Hh]it|HIT|[Pp]ills|PILLS|[Bb]lots|[Bb]lotters|[Bb]lot"

        with open(filename1, 'w') as f1:
            # for td in soup.find_all('td'):
                # for string in td.stripped_strings:
                for string in soup.stripped_strings:
                    if prev:
                        string = prev + " " + string

                    p = re.search("(([฿$€]\s?\s?[0-9]+\.?[0-9]*?)|([0-9]+\.?[0-9]*?\s?\s?[฿$€]))(.*)", string)      
                    if p:
                        js['price'] = p.group(1) 
                        string = p.group(4)
                        pc = 1

                    w = re.search("(.*?)((([0-9]+(\.[0-9]*)?\s?("+weights+")?\s?-\s?)?[0-9]+(\.[0-9]*)?\s?("+weights+"))|(\s[xX]\s?[0-9]+\s?("+weights+")?))(.*)", string)
                    if w:
                        js['quantity'] = w.group(2)
                        string = w.group(1) + w.group(11)
                        wc = 1

                    if len(string)>4:
                        if len(string)>60:
                            js['product_desc'] = string
                        elif any(x in string.lower() for x in ['price', 'product', 'order', 'buy', 'weight', 'quantity']):
                            pass
                        else:
                            js['product_name'] = string
                            nc = 1
                            pc = 0
                    else:
                        prev = string
            
                    if nc==1 and wc==1 and pc==1:
                        js['date'] = datetime.datetime.now()
                        # es.index(index=index, doc_type='product', body=js)
                        js['date'] = js['date'].strftime('%Y-%m-%d %H:%M:%S:%f')
                        json.dump(js, f1)
                        f1.write(',')
                        wc = 0
                        pc = 0

        print ("Written:", filename1)

        ########################################################################
        pages = response.xpath('//a/@href').extract()
        webAll[url] = [page for page in pages if 'http' in page]  # add relative links also
        
        b = 0
        for page in webAll[url]:            
            if self.breadth!=0 and b>=self.breadth:
                break
            if ".onion" in page and page not in crawled:
                print (page, "---->", b)
                webCrawl[url].append(page)
                page = response.urljoin(page)
                
                yield scrapy.Request(page, callback=self.parse, meta=self.proxy)
                b += 1

webAll = {} 
webCrawl = {}
crawled = []
crawl_prefix = []  

# index = "darkweb_crawler"
# es = Elasticsearch(['http://:6968/'])
# es.indices.create(index=index, ignore=400)

tic = time.time()

with open('market_query', 'r') as f:
    jsQ = json.loads(f.read())

print (jsQ['fields'])

runner = CrawlerRunner({'DEPTH_LIMIT': int(jsQ['depth'])})
d = runner.crawl(Venom, fields=jsQ['fields'],  allowed_domains=jsQ['allowed_domains'], breadth=int(jsQ['breadth']), name=jsQ['name'])
d.addBoth(lambda _: reactor.stop())
reactor.run()

toc = time.time()
print (toc-tic, "seconds")