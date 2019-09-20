# coding=utf-8
import sys, re
import unicodedata

aioVer = "1.3"
aioReleaseDate = "2019-09-20"
userOS = sys.platform

try:
	import amiga
	userOS = "os4"
except:
	pass

class cmnHandler:
	def showIntroText(self):
		print "aiostreams v%s (%s) - Developed by George Sokianos\n" % (aioVer, aioReleaseDate)

	def getUserOS(self):
		return userOS
		
	def uniStrip(self, text):
		if (userOS == 'os4'):
			return re.sub(r'[^\x00-\x7f]',r'', text)
		# text = unicodedata.normalize('NFKD', text).encode('ascii', 'xmlcharrefreplace')
		return text

	def spoofAs(self, agent):
		agents = {
			'CHROME': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
			'FIREFOX': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
			'ANDROID': 'Mozilla/5.0 (Linux; Android 7.1.1; SM-J510FN Build/NMF26X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36',
			'EDGE': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
		}

		try:
			return agents[agent]
		except KeyError:
			return None