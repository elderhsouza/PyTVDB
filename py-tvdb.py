import time
import requests

from zipfile import ZipFile
from tempfile import TemporaryFile
from bs4 import BeautifulSoup

'''
# ------------------- TODO
- output options (object or xml) see below better idea ;)
- abstract dictionaries into classes (Series, Episode, Actor)
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

	def _filter_value(self, node):
		''
		return node.string if node else None

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
				results.append({
					'tvdb_id': self._filter_value(series.seriesid),
					'title': self._filter_value(series.seriesname),
					'language': self._filter_value(series.language),
					'overview': self._filter_value(series.overview),
					'first_aired': self._filter_value(series.firstaired),
					'network': self._filter_value(series.network),
					'imdb_id': self._filter_value(series.imdb_id),
					'zap2it_id': self._filter_value(series.zap2it_id),
					'banner': self._filter_value(series.banner)
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
			'tvdb_id': self._filter_value(series.id),
			'title': self._filter_value(series.seriesname),
			'airs_day_of_week': self._filter_value(series.airs_dayofweek),
			'airs_time': self._filter_value(series.airs_time),
			'content_rating': self._filter_value(series.contentrating),
			'first_aired': self._filter_value(series.firstaired),
			'genre': self._filter_value(series.genre),
			'imdb_id': self._filter_value(series.imdb_id),
			'network': self._filter_value(series.network),
			'network_id': self._filter_value(series.networkid),
			'rating': self._filter_value(series.rating),
			'rating_count': self._filter_value(series.ratingcount),
			'runtime': self._filter_value(series.runtime),
			'overview': self._filter_value(series.overview),
			'status': self._filter_value(series.status),
			'zap2it_id': self._filter_value(series.zap2it_id),
			'language': self._filter_value(series.language),
			'actors': self._filter_value(series.actors),
			'added': self._filter_value(series.added),
			'added_by': self._filter_value(series.addedby),
			'banner': self._filter_value(series.banner),
			'fanart': self._filter_value(series.fanart),
			'poster': self._filter_value(series.poster),
			'seasons': num_seasons
		}
		return result

	def get_episodes(self, series_id, include_specials=False, include_unaired=False):
		'return a list dictionary with all episodes from a series, optionally including any specials'

		data = self._get_data(series_id)
		episodes = data['episodes']

		results = []
		for episode in episodes:

			if not include_specials and episode.seasonnumber.string == '0': 
				continue

			air_date = time.strptime(episode.firstaired.string, '%Y-%m-%d')
			current_date = time.localtime(time.time())

			if not include_unaired and current_date < air_date:
				continue

			results.append({
				'id': self._filter_value(episode.id),
				'combined_episode_number': self._filter_value(episode.combined_episodenumber),
				'combined_season': self._filter_value(episode.combined_season),
				'dvd_chapter': self._filter_value(episode.dvd_chapter),
				'dvd_disc_id': self._filter_value(episode.dvd_discid),
				'dvd_episode_number': self._filter_value(episode.dvd_episodenumber),
				'dvd_season': self._filter_value(episode.dvd_season),
				'director': self._filter_value(episode.director),
				'ep_img_flag': self._filter_value(episode.epimgflag),
				'episode_name': self._filter_value(episode.episodename),
				'episode_number': self._filter_value(episode.episodenumber),
				'first_aired': self._filter_value(episode.firstaired),
				'guest_stars': self._filter_value(episode.gueststars),
				'imdb_id': self._filter_value(episode.imdb_id),
				'language': self._filter_value(episode.language),
				'overview': self._filter_value(episode.overview),
				'production_code': self._filter_value(episode.productioncode),
				'rating': self._filter_value(episode.rating),
				'rating_count': self._filter_value(episode.ratingcount),
				'season_number': self._filter_value(episode.seasonnumber),
				'writer': self._filter_value(episode.writer),
				'absolute_number': self._filter_value(episode.absolute_number),
				'airs_after_season': self._filter_value(episode.airsafter_season),
				'airs_before_episode': self._filter_value(episode.airsbefore_episode),
				'airs_before_season': self._filter_value(episode.airsbefore_season),
				'filename': self._filter_value(episode.filename),
				'last_updated': self._filter_value(episode.lastupdated),
				'season_id': self._filter_value(episode.seasonid),
				'series_id': self._filter_value(episode.seriesid),
				'thumb_added': self._filter_value(episode.thumb_added),
				'thumb_width': self._filter_value(episode.thumb_width),
				'thumb_height': self._filter_value(episode.thumb_height)
			})

		return results
		

	def get_episodes_by_season(self, series_id, season_number):
		pass

	def get_episode_by_number(self, series_id, season_number, episode_number):
		pass

	def get_episode_by_id(self, series_id, episode_id):
		pass

	def get_actors(self, series_id):
		pass

	def get_actor(self, actor_id):
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
# print tvdb.get_series('121361')
# print tvdb.get_series('81189')
# print tvdb.get_series(81189)

# episodes = tvdb.get_episodes(121361)
# for ep in episodes:
# 	print '%s - S%sE%s: %s' % (ep['first_aired'], ep['season_number'], ep['episode_number'], ep['episode_name'])

# print tvdb.get_series('121361')
# print tvdb.get_series(90989999999999)

