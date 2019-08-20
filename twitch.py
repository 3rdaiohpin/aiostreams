#!python
try:
	import amiga
	amigaMode = True
except:
	amigaMode = False
import urllib, urllib2, sys, argparse, re, string
import simpleM3U8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random
import cfg

clientId = "k5y7u3ntz5llxu22gstxyfxlwcz10v"

_url_re = re.compile(r"""
    http(s)?://
    (?:
        (?P<subdomain>[\w\-]+)
        \.
    )?
    twitch.tv/
    (?:
        videos/(?P<videos_id>\d+)|
        (?P<channel>[^/]+)
    )
    (?:
        /
        (?P<video_type>[bcv])(?:ideo)?
        /
        (?P<video_id>\d+)
    )?
    (?:
        /(?:clip/)?
        (?P<clip_name>[\w]+)
    )?
""", re.VERBOSE)

class twitchAPIHandler:
	def __init__(self):
		self.baseurl = 'https://api.twitch.tv'

		return

	def call(self, endpoint, query = None):
		queryArgs = None
		if (query):
			queryArgs = urllib.urlencode(query)
		url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)
		
		request = urllib2.Request(url)
		request.add_header('Accept', 'application/vnd.twitchtv.v4+json')
		request.add_header('Client-ID', clientId)
		try:
			response = urllib2.urlopen(request)
			retData = json.load(response)
			response.close()
			return retData
		except URLError, e:
			print e.reason
		
		return None

	def getChannelInfoByName(self, channelName):
		endpoint = "kraken/channels/%s.json" % (channelName)
		retData = self.call(endpoint)

		return retData

	def getStreamsByChannel(self, channelName):
		endpoint = "kraken/streams/%s.json" % (channelName)
		retData = self.call(endpoint)

		return retData

	def getAccessTokenByChannel(self, channelName):
		endpoint = "api/channels/%s/access_token.json" % (channelName)
		retData = self.call(endpoint)

		return retData

	def getVideoInfoByID(self, videoId):
		endpoint = "kraken/videos/%s.json" % (videoId)
		retData = self.call(endpoint)

		return retData

	def getAccessTokenByVideo(self, videoId):
		endpoint = "api/vods/%s/access_token.json" % (videoId)
		retData = self.call(endpoint)

		return retData

	def searchByGameTitle(self, title):
		endpoint = "kraken/search/streams"
		query = {
			"query": title
		}
		retData = self.call(endpoint, query)

		return retData

class usherHandler:
	def __init__(self):
		# self.baseurl = 'https://usher.ttvnw.net'
		self.baseurl = 'https://usher.twitch.tv'

		return None

	def call(self, endpoint, query = None):
		queryArgs = None
		if (query):
			queryArgs = urllib.urlencode(query)
		url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)
		request = urllib2.Request(url)

		try:
			response = urllib2.urlopen(request)
			retData = response.read()
			response.close()
			return retData
		except URLError, e:
			print e.reason
		
		return None

	def getChannelStreams(self, channelName, sig, token):
		endpoint = "api/channel/hls/%s" % (channelName)
		query = {
			"player": "twitchweb",
			"type": "any",
			"allow_source": "true",
			"allow_audio_only": "true",
			"allow_spectre": "false",
			"p": int(random() * 999999),
			"sig": sig,
			"token": token
		}
		retData = self.call(endpoint, query)

		return retData

	def getVideoStreams(self, videoId, sig, token):
		endpoint = "vod/%s" % (videoId)
		query = {
			"player": "twitchweb",
			"type": "any",
			"allow_source": "true",
			"allow_audio_only": "true",
			"allow_spectre": "false",
			"p": int(random() * 999999),
			"sig": sig,
			"token": token
		}
		retData = self.call(endpoint, query)

		return retData


class helpersHandler:

	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)

		if (types['channel']):
			return {'type': 'channel', 'id': types['channel']}

		if (types['videos_id']):
			return {'type': 'video', 'id': types['videos_id']}

		return None

	def m3u8GetModel(self, data):
		m3u8Data = m3u8.loads(data)
		return m3u8Data.data
	
	def m3u8GetPlaylists(self, data):
		m3u8Model = self.m3u8GetModel(data)

		return m3u8Model['playlists']
	
	def m3u8GetMedia(self, data):
		m3u8Model = self.m3u8GetModel(data)
		
		return m3u8Model['media']

	def getPrefferedVideoURL(self, data):
		sm3u8Parser = sm3u8.parseHandler()
		# playlists = self.simpleM3U8Parser(data)
		playlists = sm3u8Parser.parse(data)
	
		for quality in cfg.twitchQualityWeight:
			for idx in playlists:
				if (quality == playlists[idx]['video']):
					return playlists[idx]['uri']
		
		return None

	def encodeToken(self, token):
		encToken = string.replace(token, '"', "%22")
		encToken = string.replace(encToken, "{", "%7B")
		encToken = string.replace(encToken, "}", "%7D")

		return encToken

def main(argv):
	twitchApi = twitchAPIHandler()
	usherApi = usherHandler()
	helpers = helpersHandler()
	video = {'type': ''}
	searchMode = False
	playlists = dict()

	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses twitch.tv API to get information about channels/videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url from twitch.tv')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	argParser.add_argument('-s', '--search', action='store', dest='search', help='Search for available streams based on game title')
	args = argParser.parse_args()

	if (args.url):
		twitchURL = args.url
		video = helpers.getVideoType(args.url)
	if (args.quality):
		cfg.twitchQualityWeight.insert(0, args.quality)
	if (args.search):
		gameTitle = args.search
		searchMode = True

	if (video['type'] == 'channel'):
		channelName = video['id']
			
		streams = twitchApi.getStreamsByChannel(channelName)
		if (streams):
			if (streams['stream']):
				if (streams['stream']['stream_type'] == 'live'):
					accessToken = twitchApi.getAccessTokenByChannel(channelName)
					m3u8Response = usherApi.getChannelStreams(channelName, accessToken['sig'], accessToken['token'])
					if (m3u8Response):
						uri = helpers.getPrefferedVideoURL(m3u8Response)
						if uri:
							if cfg.verbose:
								print "%s" % (uri)
							if cfg.autoplay:
								# print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
								if amigaMode:
									amiga.system( "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
						else:
							print "Not valid stream found"
					else:
						print "There was an error with the usherApi"
			else:
				print "There is no Live stream for the channel: %s" % (channelName)


	if (video['type'] == 'video'):
		videoId = video['id']

		streams = twitchApi.getVideoInfoByID(videoId)
		if (streams):
			if (streams['viewable'] == 'public'):
				accessToken = twitchApi.getAccessTokenByVideo(videoId)
				m3u8Response = usherApi.getVideoStreams(videoId, accessToken['sig'], accessToken['token'])
				uri = helpers.getPrefferedVideoURL(m3u8Response)
				if uri and cfg.autoplay:
					print "%s %s %s" % (cfg.vPlayer, uri, cfg.vPlayerArgs)
					amiga.system( "%s %s %s" % (cfg.vPlayer, uri, cfg.vPlayerArgs) )
				
		else:
			print "There is no video available with ID: %s" % (videoId)

	if (searchMode):
		streamList = twitchApi.searchByGameTitle(gameTitle)
		for stream in streamList['streams']:
			channel = stream['channel']
			print "%-20s\t %10s\t %-s\t %-10s\t %-50s\t %-s - \"%-s\"" % (channel['display_name'].encode('unicode_escape'), stream['viewers'], stream['stream_type'], channel['language'], channel['url'], stream['game'].encode('unicode_escape'), channel['status'].encode('unicode_escape'))
			#print "%-20s\t %10s\t %-s\t %-10s\t %-50s\t " % (channel['display_name'].encode('unicode_escape'), stream['viewers'], stream['stream_type'], channel['language'], channel['url'])


	# TODO: The following list is temporary for tests. This will be removed
	# https://www.twitch.tv/bnepac
	# https://www.twitch.tv/videos/464055415
	# channels = [
	# 	"riotgamesoce",
	# 	"amigabill",
	# 	"haysmaker64",
	# 	"overwatchleague"
	# ]
	# channelName = channels[1]


	
	sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])
