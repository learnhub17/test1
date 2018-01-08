import datetime
import time
import json
import os

import feedparser
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.http import HtmlResponse
from twisted.internet import reactor

from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup

class Carnage(scrapy.Spider):
    name = "carnage"
    proxy = {'proxy': 'http://:8118'}  # {'proxy': "http://:8118"}
    X = 0
    
    def start_requests(self): 
        for url in self.urls:
            print ("---------------"+url+"----------------")
            yield scrapy.Request(url=url, callback=self.check, meta=self.proxy)

    def check(self, response):
        print ("Checking:", response, "~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        soup = BeautifulSoup(response.body, "html.parser")
        xml = soup.find('html')
        if not xml:
            return self.parseY(response)
        else:
            return self.find(response)
            
    def find(self, response): 
        soup = BeautifulSoup(response.body, "html.parser")
        url = response.url
        print ("Not RSS:", url, "\nFinding...")
        
        links = []
        atom_links = soup.find_all('link',type='application/atom+xml')   
        rss_links = soup.find_all('link', type='application/rss+xml')

        if atom_links:
            links += atom_links
        if rss_links:
            links += rss_links

        feed_list = []
        if links:
            for link in links:
                href = link.get('href')
                if not href.startswith('http'):
                    feed_list.append(url+href)
                    feed_list.append('/'.join(url.split('/')[:3])+'/'+href)
                feed_list.append(href)

        if not feed_list:
            print ("***AUTODISCOVERY FAILED***")
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    if 'rss' in href or 'atom' in href or 'feed' in href:
                        if not href.startswith('http'):
                            feed_list.append(url+href)
                            feed_list.append('/'.join(url.split('/')[:3])+'/'+href)
                        feed_list.append(href)

        if feed_list:
            feed_list = set(feed_list)
            for feed in feed_list:
                print ("found:", feed)
                yield scrapy.Request(url=feed, callback=self.check, meta=self.proxy)
        else:
            print ("No RSS Found... (%s)" % url)


    def parseY(self, response):
        self.X += 1
        print (self.X, "Is RSS:", response, "++++++++++++++++++++++++++++++")
        url = response.url
        d = feedparser.parse(url)

        js = {}
        js['feed_url'] = d.feed.link
        js['feed_title'] = d.feed.title
        # js['feed_description'] = d.feed.description
        # js['feed_published'] = d.feed.published

        file = os.path.join('rss_data', js['feed_title']+'.txt')

        with open(file, 'w') as f:
            print ("Len:", len(d.entries))
            for entry in d.entries:
                # print (entry)
                js['entry_url'] = entry.link
                js['entry_title'] = entry.title
                # js['entry_id'] = entry.id
                # try:
                #     js['summary'] = []
                #     for i, content in enumerate(entry.content):
                #         js['summary'].append(content['value']) 
                # except:
                #     pass
                js['published'] = entry.published
                # try:
                #     js['published'] = datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z") 
                # except:                                                  # Thu, 07 Dec 2017 02:49:35 GMT            
                #     js['published'] = datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")

                js['crawled'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')

                json.dump(js, f)
                f.write(',')
                
        print (self.X, "Written in:", file)

# index = "rss_crawler"
# es = Elasticsearch(['http://:6968/'])
# es.indices.create(index=index, ignore=400)

tic = time.time()

with open('rss_query', 'r') as f:
    jsQ = json.loads(f.read())

runner = CrawlerRunner({'DEPTH_LIMIT': 2})
d = runner.crawl(Carnage, urls=jsQ['urls'])

d.addBoth(lambda _: reactor.stop())
reactor.run()

toc = time.time()
print (toc-tic, "seconds")
