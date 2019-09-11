#!/usr/bin/env python
# coding=utf-8
import cfg, cmn
import urllib, urllib2, sys, argparse, re, string
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random
try:
	import amiga
	userOS = "os4"
except:
	pass

cmnHandler = cmn.cmnHandler()

_url_re = re.compile(r"""
	http(s)?://(\w+.)?skaitv\.gr/
    (?:
		episode/(?P<categ>[^/?]+)
		/
		(?P<caption2>[^/?]+)
		/
		(?P<caption>[^/?]+)
	)
    (?:
		/
		(?P<clip>[^/?]+)
    )?
""", re.VERBOSE)

class skaiAPIHandler:
	def __init__(self):
		self.baseurl = 'http://www.skaitv.gr/json'

		return

	def getURL(self, url):
		request = urllib2.Request(url)
		try:
			response = urllib2.urlopen(request)
			retData = response.read()
			response.close()
			return retData
		except URLError, e:
			print e
		
		return None

	def call(self, endpoint, query = None):
		queryArgs = None
		if (query):
			queryArgs = urllib.urlencode(query)
		url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)
		return self.getURL(url)

	def getVideoInfo(self, parsedUrl):
		endpoint = "episode.php"
		query = {
			"caption": "no",
			"show_caption": parsedUrl['caption'],
			"epanalipsi": "",
			"cat_caption2": parsedUrl['caption2']
		}
		responseData = self.call(endpoint, query)
		if responseData:
			return json.loads(responseData)
		return None


class helpersHandler:
	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)

		if (types['caption'] and types['caption2']):
			return {'type': 'video', 'caption': types['caption'], 'caption2': types['caption2'], 'clip': types['clip']}

		# TODO: Support Live streams
		#if (types['videos_id']):
		#	return {'type': 'live', 'id': types['videos_id'], 'channel': types['channel']}

		return None

	def buildM3U8Uri(self, media):
		return "http://videostream.skai.gr/%s.m3u8" % (media)
		

def main(argv):
	skaiApi = skaiAPIHandler()
	helpers = helpersHandler()

	if len(argv) == 0:
		print "No arguments given. Use skaitv.py -h for more info.\nThe script must be used from the shell."
		sys.exit()
		
	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses skaitv.gr to get information about videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video url from skaitv.gr')
	argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
	args = argParser.parse_args()

	if (args.silence != True):
		cmnHandler.showIntroText()
	if (args.url):
		skaiURL = args.url
		video = helpers.getVideoType(args.url)

	if (video['type'] == 'video'):
		videoInfo = skaiApi.getVideoInfo(video)

		if videoInfo['episode']:
			uri = None
			for episode in videoInfo['episode']:
				if video['clip'] == None and episode['media_type'] == "1":
					uri = helpers.buildM3U8Uri(episode['media_item_file'])
					break
				if video['clip'] != None and episode['mi_caption'] == video['clip']:
					uri = helpers.buildM3U8Uri(episode['media_item_file'])
					break

			if (uri):
				m3u8Response = skaiApi.getURL(uri)

				if m3u8Response:
					if cfg.verbose and (args.silence != True):
						print "%s" % (uri)
					if cfg.autoplay:
						# print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
						if (cmnHandler.getUserOS() == 'os4'):
							amiga.system( "Run <>NIL: %s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
				else:
					print "Not valid video playlist found"
		else:
			print "There is no video available!"

		sys.exit()
	
	sys.exit()

if __name__ == "__main__":
	main(sys.argv[1:])