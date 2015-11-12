

import json


def fixSmartQuotes(text):
	text = text.replace(r"\'", "'")
	text = text.replace(r'\"', '"')
	text = text.replace(r"’", "'")
	text = text.replace(r"‘", "'")
	text = text.replace(r"“", '"')
	text = text.replace(r"”", '"')
	return text

def fix_dict(inRelease):
	for key in inRelease.keys():
		if isinstance(inRelease[key], str):
			inRelease[key] = fixSmartQuotes(inRelease[key])
	return inRelease

def buildReleaseMessage(raw_item, series, vol, chap=None, frag=None, postfix='', author=None, tl_type='translated', extraData={}, beta=False):
	'''
	Special case behaviour:
		If vol or chapter is None, the
		item in question will sort to the end of
		the relevant sort segment.
	'''
	ret = {
		'srcname'   : raw_item['srcname'],
		'series'    : series,
		'vol'       : vol,
		'chp'       : packChapterFragments(chap, frag),
		'published' : raw_item['published'],
		'itemurl'   : raw_item['linkUrl'],
		'postfix'   : postfix,
		'author'    : author,
		'tl_type'   : tl_type,

		# "beta" items are optionally filtered client-end to allow
		# testing in my dev env without having the feed outputs go through
		# to the prod env
		'beta'      : beta,
	}

	for key, value in extraData.items():
		assert key not in ret
		ret[key] = value

	ret = fix_dict(ret)
	return ret


def packChapterFragments(chapStr, fragStr):
	if not chapStr and not fragStr:
		return None
	if not fragStr:
		return chapStr

	# Handle cases where the fragment is present,
	# but the chapStr is None
	if chapStr == None:
		chapStr = 0

	chap = float(chapStr)
	frag = float(fragStr)
	return '%0.2f' % (chap + (frag / 100.0))




def createReleasePacket(data, beta=False):
	'''
	Release packets can have "extra" data, so just check it's long enough and we have the keys we expect.	'''

	expect = ['srcname', 'series', 'vol', 'chp', 'published', 'itemurl', 'postfix', 'author', 'tl_type']
	data = fix_dict(data)

	assert len(expect) <= len(data), "Invalid number of items in release packet! Expected: '%s', received '%s'" % (expect, data)
	assert all([key in data for key in expect]), "Invalid key in release message! Expect: '%s', received '%s'" % (expect, list(data.keys()))

	ret = {
		'type' : 'parsed-release',
		'data' : data,

		# "beta" items are optionally filtered client-end to allow
		# testing in my dev env without having the feed outputs go through
		# to the prod env
		'beta'      : beta,
	}
	return json.dumps(ret)


def sendSeriesInfoPacket(data, beta=False):

	expect = ['title', 'author', 'tags', 'homepage', 'desc', 'tl_type', 'sourcesite']
	data = fix_dict(data)

	assert len(expect) == len(data),             "Invalid number of items in metadata packet! Expected: '%s', received '%s'" % (expect, data)
	assert all([key in data for key in expect]), "Invalid key in metadata message! Expect: '%s', received '%s'" % (expect, list(data.keys()))

	ret = {
		'type' : 'series-metadata',
		'data' : data,

		# "beta" items are optionally filtered client-end to allow
		# testing in my dev env without having the feed outputs go through
		# to the prod env
		'beta'      : beta,
	}
	return json.dumps(ret)
