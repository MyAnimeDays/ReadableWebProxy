


import runStatus
runStatus.preloadDicts = False

from . import ProcessorBase


import feedparser
import bs4
import json
import calendar
import WebMirror.OutputFilters.rss.FeedDataParser

# import TextScrape.RelinkLookup
# import TextScrape.RELINKABLE as RELINKABLE


import WebMirror.processor.HtmlProcessor


########################################################################################################################
#
#	##     ##    ###    #### ##    ##     ######  ##          ###     ######   ######
#	###   ###   ## ##    ##  ###   ##    ##    ## ##         ## ##   ##    ## ##    ##
#	#### ####  ##   ##   ##  ####  ##    ##       ##        ##   ##  ##       ##
#	## ### ## ##     ##  ##  ## ## ##    ##       ##       ##     ##  ######   ######
#	##     ## #########  ##  ##  ####    ##       ##       #########       ##       ##
#	##     ## ##     ##  ##  ##   ###    ##    ## ##       ##     ## ##    ## ##    ##
#	##     ## ##     ## #### ##    ##     ######  ######## ##     ##  ######   ######
#
########################################################################################################################




class RssProcessor(WebMirror.OutputFilters.rss.FeedDataParser.DataParser):


	wanted_mimetypes = [
							'application/atom+xml',
							'application/rdf+xml',
							'application/rss+xml',
							'application/xml',
							'text/xml',
						]
	want_priority    = 50

	loggerPath = "Main.Text.RssProcessor"

	_no_ret = False

	@staticmethod
	def wantsFromContent(content):
		try:
			# Check if the feed has a version
			feed = feedparser.parse(content)
			return bool(feed['version'])
		except Exception:
			return False

	def __init__(self, **kwargs):

		super().__init__(**kwargs)

		# We're inheriting from a filter (which implicitly sets _no_ret),
		# but we /do/ return content (Rss is a oddball filter instance), so
		# therefore we reset _no_ret after calling the parent initializer
		self._no_ret = False

		self.kwargs     = kwargs

		self.loggerPath = kwargs['loggerPath']+".RssProcessor"
		self.pageUrl    = kwargs['pageUrl']

		self.content    = kwargs['pgContent']
		self.type       = kwargs['type']

		self.log.info("Processing RSS Item")


	# @profile
	def parseFeed(self, rawFeed):
		return feedparser.parse(rawFeed)




	def extractFeedContents(self, feedUrl, contentDat):
		# TODO: Add more content type parsing!

		# So the complete fruitcakes at http://gravitytales.com/feed/ are apparently
		# embedding their RSS entries in a CDATA field in their feed, somehow.
		# Anyways, I think they probably broke wordpress. However, they're then breaking
		# /my/ stuff, so work around their fucked up feed format.
		if isinstance(contentDat, str):
			contentDat = [{
				'value' : contentDat,
				'type'  : 'text/html'
			}]
		if len(contentDat) != 1:
			print(contentDat)
			raise ValueError("How can one post have multiple contents?")

		contentDat = contentDat[0]


		# params = self.kwargs.copy()


		# params['pgContent'] = contentDat['value']
		# params['mimeType']  = contentDat['type']


		# # baseUrls, pageUrl, pgContent, loggerPath, relinkable
		# scraper = WebMirror.processor.HtmlProcessor.HtmlPageProcessor(**params)

		# extracted = scraper.extractContent()
		# assert contentDat['type'] == 'text/html'
		# content = extracted['contents']
		content = "Disabled?"

		# Use a parser that doesn't try to generate a well-formed output (and therefore doesn't insert
		# <html> or <body> into content that will be only a part of the rendered page)
		soup = bs4.BeautifulSoup(content, "html.parser")



		if soup.html:
			soup.html.unwrap()
		if soup.body:
			soup.body.unwrap()

		try:
			cont = soup.prettify()
		except RuntimeError:
			try:
				cont = str(soup)
			except RuntimeError:
				cont = '<H2>WARNING - Failure when cleaning and extracting content!</H2><br><br>'
				cont += content


		return content


	def processFeed(self, feed, feedUrl):


		meta = feed['feed']
		entries = feed['entries']

		ret = []

		for entry in entries:


			# if entry['title'].startswith('User:'):
			# 	# The tsuki feed includes changes to user pages. Fuck that noise. Ignore that shit.
			# 	continue

			if not 'guid' in entry:
				# print("if not 'guid' in entry:")
				continue
			if not "authors" in entry:
				# print('if not "authors" in entry:')
				continue

			item = {}
			item['feedtype'] = self.type

			item['title']    = entry['title']
			item['guid']     = entry['guid']
			item['linkUrl']  = entry['link']
			item['authors']  = entry['authors']



			if 'updated_parsed' in entry:
				item['updated']   = calendar.timegm(entry['updated_parsed'])

			if 'published_parsed' in entry:
				item['published'] = calendar.timegm(entry['published_parsed'])

			if not 'published' in item or ('updated' in item and item['published'] > item['updated']):
				item['published'] = item['updated']

			if not 'updated' in item:
				item['updated']   = 0

			item['tags']    = []
			if 'tags' in entry:
				for tag in entry['tags']:
					item['tags'].append(tag['term'])


			if 'content' in entry:
				item['contents'] = self.extractFeedContents(feedUrl, entry['content'])
			elif 'summary' in entry:
				item['contents'] = self.extractFeedContents(feedUrl, entry['summary'])
			else:
				self.log.error('Empty item in feed?')
				self.log.error('Feed url: %s', feedUrl)
				continue


			# print("Keys: ", list(item.keys()))

			# processFeedData() call has to be /before/ we convert the tags to a json object.
			self.processFeedData(item)


			assert(isinstance(item['published'], (float, int))), "Wrong type for item['published']. Expected '%s', received '%s'" % ((float, int), type(item['published']))
			assert(isinstance(item['updated'], (float, int, type(None)))), "Wrong type for item['updated']. Expected '%s', received '%s'" % ((float, int, type(None)), type(item['updated']))

			# print("Keys: ", list(item.keys()))
			ret.append(item)
		return ret



	def extractContent(self):
		print("Rss extracting content!")


		feed = self.parseFeed(self.content)
		data = self.processFeed(feed, self.pageUrl)

		# print(data)
		# self.insertFeed(tableName, tableKey, pluginName, feedUrl, data, badwords)


		ret = {}
		# No links here

		ret['rss-content'] = (data)
		return ret




def testJobFromUrl(url):
	import datetime
	import WebMirror.database
	return WebMirror.database.WebPages(
				state     = 'fetching',
				url       = url,
				starturl  = url,
				netloc    = "wat",
				distance  = WebMirror.database.MAX_DISTANCE-2,
				is_text   = True,
				priority  = WebMirror.database.DB_REALTIME_PRIORITY,
				type      = "unknown",
				fetchtime = datetime.datetime.now(),
				)



def test():
	print("Test mode!")
	import logSetup
	import WebMirror.rules
	import WebMirror.Engine
	import multiprocessing
	logSetup.initLogging()

	c_lok = cookie_lock = multiprocessing.Lock()
	engine = WebMirror.Engine.SiteArchiver(cookie_lock=c_lok)



	url = 'http://taulsn.wordpress.com/feed/'

	job = testJobFromUrl(url)
	engine.dispatchRequest(job)


	url = 'http://turb0translation.blogspot.com/feeds/posts/default'
	job = testJobFromUrl(url)
	engine.dispatchRequest(job)


	url = 'http://www.w3schools.com/xml/note.xml'
	job = testJobFromUrl(url)
	engine.dispatchRequest(job)


if __name__ == "__main__":
	test()

