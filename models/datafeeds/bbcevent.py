import urllib2

try:
	import simplejson
except:
	import json as simplejson

import re


class BbcEventFeed:
	strBbcFeed = 'http://www.bbc.co.uk/sport/0/hi/english/static/football/statistics/collated/videprinter.json'

	def _fetchRawData(self):
		return urllib2.urlopen(self.strBbcFeed).read()

	# BBC feed includes html comments which unfortunately
	# breaks the python json library, so strip them out
	def stripHtmlComments(self, strData):
		# Remove conditional rubbish at end of feed
		parsed = re.sub(r'<\!--#if.*', '}', strData)
		# Remove include at top of feed
		return re.sub(r'<\!--#include[a-z =\"\/\\\$_\.]*-->', '', parsed)

	def getEvents(self):
		strRaw  = self._fetchRawData()
		strData = self.stripHtmlComments(strRaw)
		dctData = simplejson.loads(strData)
		return dctData['footballVideprinter']['matchEvent'] if 'matchEvent' in dctData['footballVideprinter'] else None
