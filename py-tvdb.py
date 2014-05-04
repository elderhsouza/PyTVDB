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
	cache = {}

	def __init__(self, api_key, language='en'):
		''
		self.api_key = api_key
		self.language = language

	def _is_cached(self, series_id):
		''
		return str(self.cache_id) == str(series_id)

	def _clear_cache(self):
		''
		self.cache_id = None
		self.cache = {}

	# TODO Implement TypeArgumentException, IOException, BadZipFileException, HTTP404Exception, ConnectionException
	def _get_data(self, series_id):
		'get series(tv show) information from thetvdb.com and cache the results'

		series_id = str(series_id)

		if self._is_cached(series_id):
			data = self.cache

		else:
			response = requests.get('%s/api/%s/series/%s/all/%s.zip' % (self.mirror, self.api_key, series_id, self.language))
			if response.status_code != 200:
				return

			self._clear_cache()

			with TemporaryFile() as tmp_file:
				tmp_file.write(response.content)

				with ZipFile(tmp_file, 'r') as zip_file:
					
					with zip_file.open('%s.xml' % (self.language)) as xml_info:
						content = BeautifulSoup(xml_info.read())

						self.cache['series'] = content.find('series')
						self.cache['episodes'] = content.find_all('episode')

					with zip_file.open('actors.xml') as xml_actors:
						self.cache['actors'] = BeautifulSoup(xml_actors.read())

					with zip_file.open('banners.xml') as xml_banners:
						self.cache['banners'] = BeautifulSoup(xml_banners.read())

		self.cache_id = series_id
		data = self.cache

		return data

	def search(self, query):
		'search thetvdb.com database for series(tvshow) containing the query and return a list of dictionaries with the results'

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
					'zap2it_id': filter_node(series.zap2it_id),
					'banner': filter_node(series.banner)
				})
		else :
			return

		return results

	def get_series(self, series_id) :
		'get series(tv show) info from thetvdb.com and return a dictionary with the results'

		data = self._get_data(series_id)

		series = data['series']
		num_seasons = data['episodes'][-1].seasonnumber.string

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
			'seasons': num_seasons
		}
		return result

		# print num_seasons
		# seasons = max([int(s.string) for s in data.find_all('seasonnumber')])
		# print seasons

		# print data['series']
		# print data['episodes']

		# print data['series']
		# print data['episodes']

		# series = data.find('series')

		# seasons = max([int(s.string) for s in data.find_all('seasonnumber')])
		# # TODO maybe replace bs for lxml for css selectors like :last-child ?

		

	def get_all_episodes(self, series_id, include_specials=False):
		pass

	def get_episodes_by_season(self, series_id, season_number):
		pass

	def get_episode_by_number(self, series_id, season_number, episode_number):
		pass

	def get_episode_by_id(self, series_id, episode_id):
		pass

	def get_actors(self, series_id):
		pass

	# server_time 1399036356
	def get_updates(self, server_time, *series_id):
		pass

	#TODO implement graphics request
	def get_graphics(self, series_id):
		pass

	def get_banners(self, series_id):
		pass

	def get_posters(self, series_id):
		pass

	def get_fanart(self, series_id):
		pass

	def get_series_posters(self, series_id):
		pass

	def get_season_posters(self, series_id, season_number):
		pass
		

#------------ TESTING
# series_id: ['game of thrones': 121361, 'breaking bad': 81189]

tvdb = PyTVDB('D229EEECFE78BA5F')

# print tvdb.search('thrones')

# print tvdb.get_series(121361)
print tvdb.get_series('121361')
print tvdb.get_series('81189')
print tvdb.get_series(81189)
# print tvdb.get_series('121361')
# print tvdb.get_series(90989999999999)

