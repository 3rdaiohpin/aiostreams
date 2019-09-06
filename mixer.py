#!python
import cfg, cmn
import urllib, urllib2, sys, argparse, re, string
import simplem3u8 as sm3u8
import simplejson as json
from urllib2 import Request, urlopen, URLError
from random import random

clientId = "b1cb746d2751f467188edbb12997d4412b711011f640ce04"	

_url_re = re.compile(r"""
	http(s)?://(\w+.)?mixer\.com/
    (?:
		(?P<channel>[^/?]+)
	)
    (?:
        (?:\?vod=)?
        (?P<video_id>[\w]+)
    )?
""", re.VERBOSE)

class mixerAPIHandler:
	def __init__(self):
		self.baseurl = 'https://mixer.com/api/v1'

		return

	def call(self, endpoint, query = None):
		queryArgs = None
		if (query):
			queryArgs = urllib.urlencode(query)
		url = "%s/%s?%s" % (self.baseurl, endpoint, queryArgs)

		request = urllib2.Request(url)
		request.add_header('Client-ID', clientId)
		try:
			response = urllib2.urlopen(request)
			retData = response.read()
			response.close()
			return retData
		except URLError, e:
			print e
		
		return None

	def getChannelInfoByName(self, channelName):
		endpoint = "channels/%s" % (channelName)
		responseData = self.call(endpoint)
		if responseData:
			return json.loads(responseData)
		return None

	def getStreamsByChannelID(self, channelID):
		endpoint = "channels/%d/manifest.m3u8" % (channelID)
		query = {
			"cdn": "false"
		}
		return self.call(endpoint, query)

	def getTopStreamsByGameID(self, gameID, page = 0, limit = 50):
		endpoint = "channels"
		query = {
			"order": "viewersCurrent:DESC",
			"where": "typeId:eq:%d,online:eq:true" % (gameID),
			"limit": limit,
			"page": page
		}
		responseData = self.call(endpoint, query)
		if responseData:
			return json.loads(responseData)
		return None

	def getVideoInfoByID(self, videoId):
		endpoint = "recordings/%s" % (videoId)
		responseData = self.call(endpoint)
		if responseData:
			return json.loads(responseData)
		return None

	def searchByGameTitle(self, title, page = 0, limit = 50):
		endpoint = "types"
		query = {
			"order": "viewersCurrent:DESC",
			"where": "name:eq:%s" % (title),
			"limit": limit,
			"page": page
		}
		
		responseData = self.call(endpoint, query)
		if responseData:
			return json.loads(responseData)
		return None
	
	def getTopStreams(self, page = 0, limit = 50):
		endpoint = "channels"
		query = {
			"order": "viewersCurrent:DESC",
			"where": "online:eq:true",
			"limit": limit,
			"page": page
		}
		responseData = self.call(endpoint, query)
		return json.loads(responseData)

	def getTopGames(self, page = 0, limit = 50):
		endpoint = "types"
		query = {
			"order": "viewersCurrent:DESC",
			"where": "parent:eq:Games",
			"limit": limit,
			"page": page
		}
		responseData = self.call(endpoint, query)
		return json.loads(responseData)

	def getVideosByChannel(self, channelID, page = 0, limit = 50):
		endpoint = "channels/%d/recordings" % (channelID)
		query = {
			"order": "createdAt:DESC",
			"limit": limit,
			"page": page
		}
		responseData = self.call(endpoint, query)
		return json.loads(responseData)

class helpersHandler:
	def parseURL(self, url):
		return _url_re.match(url).groupdict()

	def getVideoType(self, url):
		types = self.parseURL(url)

		if (types['video_id']):
			return {'type': 'video', 'id': types['video_id']}

		if (types['channel']):
			return {'type': 'channel', 'id': types['channel']}

		return None

	def getPrefferedVideoURL(self, data):
		sm3u8Parser = sm3u8.parseHandler()
		playlists = sm3u8Parser.parse(data)
		
		for quality in cfg.mixerQualityWeight:
			for idx in playlists:
				if (playlists[idx]):
					if (playlists[idx]['name'].find(quality) >= 0):
						return playlists[idx]['uri']
		
		return None

def main(argv):
	cmnHandler = cmn.cmnHandler()
	mixerApi = mixerAPIHandler()
	helpers = helpersHandler()
	playlists = dict()
	
	if len(argv) == 0:
		print "No arguments given. Use mixer.py -h for more info.\nThe script must be used from the shell."
		sys.exit()
		
	# Parse the arguments
	argParser = argparse.ArgumentParser(description='This is a python script that uses mixer.com API to get information about channels/videos for AmigaOS 4.1 and above.')
	argParser.add_argument('-u', '--url', action='store', dest='url', help='The video/channel url from mixer.com')
	argParser.add_argument('-q', '--quality', action='store', dest='quality', help='Set the preffered video quality. This is optional. If not set or if it is not available the default quality weight will be used.')
	argParser.add_argument('-ts', '--top-streams', action='store_true', default=False, dest='topstreams', help='Get a list of the current Top Live Streams, based on the number of viewers')
	argParser.add_argument('-tg', '--top-games', action='store_true', default=False, dest='topgames', help='Get a list of the current Top Games with live streams available, based on the number of viewers')
	argParser.add_argument('-sg', '--search-game', action='store', dest='searchgame', help='Search for available streams based on game title')
	argParser.add_argument('-cv', '--channel-videos', action='store_true', default=False, dest='channelvideos', help='Request the recorded videos of a channel. The -u argument is mandatory.')
	argParser.add_argument('-shh', '--silence', action='store_true', default=False, dest='silence', help='If this is set, the script will not output anything, except of errors.')
	args = argParser.parse_args()
	
	if (args.silence != True):
		cmnHandler.showIntroText()
	if (args.url):
		mixerURL = args.url
		video = helpers.getVideoType(args.url)

	if (args.quality):
		cfg.mixerQualityWeight.insert(0, args.quality)

	if (args.topstreams):
		streamList = mixerApi.getTopStreams()
		print "%-36s\t %-10s\t %-10s\t %-50s\t %s" % ('URL', 'Type', 'Viewers', 'Game', 'Title')
		print "%s" % ('-'*200)
		for stream in streamList:
			streamType = stream['type']
			streamUrl = ''.join(["https://mixer.com/", stream['token']])
			print "%-36s\t %-10s\t %-10d\t %-50s\t %s" % (streamUrl, streamType['parent'], stream['viewersCurrent'], streamType['name'], cmnHandler.uniStrip(stream['name']))

		sys.exit()

	if (args.topgames):
		gamesList = mixerApi.getTopGames()
		print "%-50s\t %-10s\t %-10s" % ('Game', 'Viewers', 'Streams')
		print "%s" % ('-'*200)
		for game in gamesList:
			print "%-50s\t %-10d\t %-10d" % (cmnHandler.uniStrip(game['name']), game['viewersCurrent'], game['online'])

		sys.exit()

	if (args.channelvideos):
		channelName = video['id']
		channelInfo = mixerApi.getChannelInfoByName(channelName)
		recordingsList = mixerApi.getVideosByChannel(channelInfo['id'])
		print "%-50s\t %-30s\t %s" % ('URL', 'Recorded at', 'Title')
		print "%s" % ('-'*200)
		for recording in recordingsList:
			streamUrl = "https://mixer.com/%s?vod=%d" % (channelName, recording['id'])
			print "%-50s\t %-30s\t %s" % (streamUrl, recording['createdAt'], cmnHandler.uniStrip(recording['name']))

		sys.exit()

	if (args.searchgame):
		gameTitle = args.searchgame
		gameData = mixerApi.searchByGameTitle(gameTitle)
		if gameData:
			print cmnHandler.uniStrip(gameData[0]['name'])
			print cmnHandler.uniStrip(gameData[0]['description'])
			print "Current Viewers: %d" % (gameData[0]['viewersCurrent'])
			print "Available Streams: %d\n" % (gameData[0]['online'])

			gameStreams = mixerApi.getTopStreamsByGameID(gameData[0]['id'])
			print "%-36s\t %-10s\t %-20s\t %-50s\t %s" % ('URL', 'Viewers', 'Type', 'Game', 'Title')
			print "%s" % ('-'*200)
			for stream in gameStreams:
				streamType = stream['type']
				streamUrl = ''.join(["https://mixer.com/", stream['token']])
				print "%-36s\t %-10d\t %-20s\t %-50s\t %s" % (streamUrl, stream['viewersCurrent'], streamType['parent'], streamType['name'], cmnHandler.uniStrip(stream['name']))
		else:
			print "No information for the game: %s" % (gameTitle)
		sys.exit()

	if (video['type'] == 'channel'):
		channelName = video['id']
		channelInfo = mixerApi.getChannelInfoByName(channelName)

		if (channelInfo):
			channelID = channelInfo['id']
			channelType = channelInfo['type']
			if (args.silence != True):
				print "Name: %s" % (cmnHandler.uniStrip(channelInfo['name']))
				print "Type: %s/%s" % (channelType['parent'], channelType['name'])
				print "Total Viewers: %d" % (channelInfo['viewersTotal'])
				print "Current Viewers: %d" % (channelInfo['viewersCurrent'])

			m3u8Response = mixerApi.getStreamsByChannelID(channelID)
			if (m3u8Response):
				uri = helpers.getPrefferedVideoURL(m3u8Response)
				if uri:
					if cfg.verbose and (args.silence != True):
						print "%s" % (uri)
					if cfg.autoplay:
						# print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
						if (cmnHandler.getUserOS() == 'os4'):
							amiga.system( "Run <>NIL: %s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
				else:
					print "Not valid stream found"
			else:
				print "There was an error with the usherApi"
		else:
			print "There is no Live stream for the channel: %s" % (channelName)

		sys.exit()

	if (video['type'] == 'video'):
		videoId = video['id']

		videoInfo = mixerApi.getVideoInfoByID(videoId)
		if (videoInfo):
			for vod in videoInfo['vods']:
				if (vod['format'] == 'hls'):
					uri = "%smanifest.m3u8" % (vod['baseUrl'])
					break

			if uri:		
				if cfg.verbose and (args.silence != True):
					print "%s" % (uri)
				if cfg.autoplay:
					# print "%s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs)
					if (cmnHandler.getUserOS() == 'os4'):
						amiga.system( "Run <>NIL: %s %s %s" % (cfg.sPlayer, uri, cfg.sPlayerArgs) )
			else:
				print "Not valid recording stream found"
		else:
			print "There is no video available with ID: %s" % (videoId)

		sys.exit()

	
	sys.exit()


if __name__ == "__main__":
	main(sys.argv[1:])
