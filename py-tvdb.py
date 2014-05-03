import requests

from zipfile import ZipFile
from tempfile import TemporaryFile
from bs4 import BeautifulSoup

'''
# ------------------- TODO
- output options (object or xml)
'''

class PyTVDB(object):
	# TODO implement data cache for subsequent queries
	
	mirror = 'http://thetvdb.com'

	cache_id = None
	data_cache = {}

	def __init__(self, api_key, language='en'):
		self.api_key = api_key
		self.language = language

	def _check_cache(self, series_id):
		return str(self.cache_id) == str(series_id)

	def _flush_cache(self):
		self.cache_id = None
		self.data_cache = {}

	def _get_data(self, series_id):
		# TODO raise TypeError?
		
		if self._check_cache(series_id):
			data = self.data_cache['series']
		else:
			response = requests.get('%s/api/%s/series/%s/all/%s.zip' % (self.mirror, self.api_key, series_id, self.language))
			if response.status_code != 200:
				return
			self._flush_cache()
			with TemporaryFile() as tmp_file:
				tmp_file.write(response.content)
				with ZipFile(tmp_file, 'r') as zip_file:
					with zip_file.open('%s.xml' % (self.language)) as xml_file:
						data = BeautifulSoup(xml_file.read())
		series = data.find('series')
		seasons = max([int(s.string) for s in data.find_all('seasonnumber')])
		# TODO maybe replace bs for lxml for css selectors like :last-child ?

		# TODO prepend image urls with the appropriate domain path
		result = {
			'tvdb_id': series.id.string,
			'title': series.seriesname.string,
			'airs_day_of_week': series.airs_dayofweek.string,
			'airs_time': series.airs_time.string,
			'content_rating': series.contentrating.string,
			'first_aired': series.firstaired.string,
			'genre': series.genre.string,
			'imdb_id': series.imdb_id.string,
			'network': series.network.string,
			'network_id': series.networkid.string,
			'rating': series.rating.string,
			'rating_count': series.ratingcount.string,
			'runtime': series.runtime.string,
			'overview': series.overview.string,
			'status': series.status.string,
			'zap2it_id': series.zap2it_id.string,
			'language': series.language.string,
			'actors': series.actors.string,
			'added': series.added.string,
			'added_by': series.addedby.string,
			'banner': series.banner.string,
			'fanart': series.fanart.string,
			'poster': series.poster.string,
			'seasons': seasons
		}
		self.cache_id = series_id
		self.data_cache['series'] = data

		return result

	def search(self, query):
		'search thetvdb.com database for shows containing the query'

		response = requests.get('%s/api/GetSeries.php?seriesname=%s' % (self.mirror, query))
		response.raise_for_status()

		data = BeautifulSoup(response.text).find_all('series')

		if len(data) > 1:
			results = []
			for series in data:
				def filter_node(node):
					return node.string if node else None

				results.append({
					'tvdb_id': filter_node(series.seriesid),
					'title': filter_node(series.seriesname),
					'language': filter_node(series.language),
					'overview': filter_node(series.overview),
					'first_aired': filter_node(series.firstaired),
					'network': filter_node(series.network),
					'imdb_id': filter_node(series.imdb_id),
					'zap2it_id': filter_node(series.zap2it_id)
				})
		else :
			return

		return results

	def get_series(self, series_id) :
		pass

	def get_all_episodes(self, series_id) :
		pass

	def get_episodes_by_season(self, series_id, season_number) :
		pass

	def get_episode(self, episode_id) :
		pass

	def get_actors(self, series_id) :
		pass

	# server_time 1399036356
	def get_updates(self, server_time, *series_id) :
		pass

	#TODO implement graphics request

	def get_graphics(self, series_id) :
		pass

	def get_banners(self, series_id) :
		pass

	def get_posters(self, series_id) :
		pass

	def get_fanart(self, series_id) :
		pass

	def get_series_posters(self, series_id) :
		pass

	def get_season_posters(self, series_id, season_number) :
		pass
		

#------------ TESTING

tvdb = PyTVDB('D229EEECFE78BA5F')
search = tvdb.search('thrones')
print search

# series = search[1]
# print series

# info = tvdb.get_series(series['tvdb_id'])
# 121361 game of thrones | 81189 breaking bad

# info = tvdb.get_series(121361) # 121361 game of thrones
# print info

# info = tvdb.get_series(121361) # 121361 game of thrones
# print info

# info = tvdb.get_series(81189) # 81189 breaking bad
# print info

# info = tvdb.get_series(81189) # 81189 breaking bad
# print info

# info = tvdb.get_series(121361) # 121361 game of thrones
# print info

# info = tvdb.get_series(9999999999999999) # mal-formed id
# print info
