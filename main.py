import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '1.2')

import urllib, operator, re
import binascii
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json

import re

def asciirepl(match):
  s = match.group()  
  return '\\u00' + match.group()[2:]
  
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def request(url):
	res = urllib.urlopen(url)
	page = res.read()[2:-10]
	p = re.compile(r'\\x(\w{2})')
	ascii_string = p.sub(asciirepl, page)
	return ascii_string
	
class dictionary(webapp.RequestHandler):
	def get(self, word):
		message = request("http://www.google.com/dictionary/json?callback=a&q=%s&sl=en&tl=en&restrict=pr,de" % word)
		
		self.response.headers['Content-Type'] = 'application/json'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		
		pyobj = json.loads(message)
		
		if "primaries" in pyobj:
			main = json.loads(message)['primaries']
			
			for i in main:
				obj = {}
					
				for o in i['terms']:
					for k,v in o.iteritems():
						if v == 'phonetic':
							obj['pronunciation'] = o['text']
					
				obj['definitions'] = []
				
				for j in main[0]['entries']:
				
					if j['type'] is "related":
						continue;
					else:
						d = {}
						d['def'] = j['terms'][0]['text']
						if "entries" in j:
							d['ex'] = j['entries'][0]['terms'][0]['text']
							if not 'example' in obj:
								obj['example'] = remove_html_tags(d['ex'])
						obj['definitions'].append(d)
			self.response.out.write( json.dumps(obj) )
		else:
			self.response.out.write(json.dumps({"success": "false", "message": "Word not found"}))
			
			
class google(webapp.RequestHandler):
	def get(self, word):
		message = request("http://www.google.com/dictionary/json?callback=a&q=%s&sl=en&tl=en&restrict=pr,de" % word)
		
		self.response.headers['Content-Type'] = 'application/json'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.out.write(message)
		
class Home(webapp.RequestHandler):
	def get(self):
		userAgent = os.environ['HTTP_USER_AGENT']
		if userAgent.find('iPhone') < 0:
			main = urlfetch.fetch("http://cardmemoriae.appspot.com/main.html")
			message = main.content
		else:
			mobile = urlfetch.fetch("http://cardmemoriae.appspot.com/mobile.html")
			message = mobile.content
			
		self.response.headers['Content-Type'] = 'text/html'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.out.write(message)
		
class Mobile(webapp.RequestHandler):
	def get(self):
		mobile = urlfetch.fetch("http://cardmemoriae.appspot.com/mobile.html")
		message = mobile.content
			
		self.response.headers['Content-Type'] = 'text/html'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.out.write(message)
			

application = webapp.WSGIApplication(
                                     [
									 ('/dictionary/(.*)', dictionary),
									 ('/google/(.*)', google),
									 ('/', Home)
									 ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()