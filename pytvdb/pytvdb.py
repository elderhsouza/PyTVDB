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

# TODO add docstrings - example below
# """
# Calculate the square root of a number.

# Args:
#     n: the number to get the square root of.
# Returns:
#     the square root of n.
# Raises:
#     TypeError: if n is not a number.
#     ValueError: if n is negative.
# """

# TODO prepend image values with full http path
def filter_node(node):
	''
	return node.string if node else None

class SeriesPreview(object):

	def __init__(self, data):
		self.id = filter_node(data.seriesid)
		self.title = filter_node(data.seriesname)
		self.language = filter_node(data.language)
		self.overview = filter_node(data.overview)
		self.first_aired = filter_node(data.firstaired)
		self.network = filter_node(data.network)
		self.imdb_id = filter_node(data.imdb_id)
		self.zap2it_id = filter_node(data.zap2it_id)
		self.banner = filter_node(data.banner)

class SeriesInfo(object):

	def __init__(self, data):
		info = data['info'].find('series')

		self.id = filter_node(info.id)
		self.title = filter_node(info.seriesname)
		self.airs_day_of_week = filter_node(info.airs_dayofweek)
		self.airs_time = filter_node(info.airs_time)
		self.content_rating = filter_node(info.contentrating)
		self.first_aired = filter_node(info.firstaired)
		self.genre = filter_node(info.genre)
		self.imdb_id = filter_node(info.imdb_id)
		self.network = filter_node(info.network)
		self.network_id = filter_node(info.networkid)
		self.rating = filter_node(info.rating)
		self.rating_count = filter_node(info.ratingcount)
		self.runtime = filter_node(info.runtime)
		self.overview = filter_node(info.overview)
		self.status = filter_node(info.status)
		self.zap2it_id = filter_node(info.zap2it_id)
		self.language = filter_node(info.language)
		self.actors = filter_node(info.actors)
		self.added = filter_node(info.added)
		self.added_by = filter_node(info.addedby)
		self.banner = filter_node(info.banner)
		self.fanart = filter_node(info.fanart)
		self.poster = filter_node(info.poster)

		self.episodes = EpisodesList(data['info'].find_all('episode'))

# TODO Implement generators
class EpisodesList(list):
	''''''
	def __init__(self, data):
		self.include_unaired = False
		self.include_specials = False

		total_episodes = 0

		for episode in data:
			self.append(EpisodeInfo(episode))
			total_episodes += 1

		self.total_episodes = total_episodes

	def _should_list_episode(self, episode, include_unaired=self.include_unaired, include_specials=self.include_specials):
		return True

	def _episodes_generator(self):
		i = 0
		while i < self.total_episodes:
			if (self.include_unaired or not self[i].is_unaired) and \
			(self.include_specials or not self[i].is_special):
				yield (i)
			i += 1

	def __iter__(self):
		return (self[i] for i in self._episodes_generator())

	def __len__(self):
 	return len(list(self._episodes_generator()))

	# TODO Implement __len__ and __contains__ methods

	# def __contains__(self):
	# 	pass

	# TODO raise OutOfBoundsError - season not found, ArgumentTypeError
	def get_season(self, season_number):
		''''''
		return [episode for episode in self
			if episode.season_number == str(season_number)]

	# TODO raise OutOfBoundsError - episode not found, ArgumentTypeError
	def get_episode(self, season_number, episode_number):
		''''''
		return self.get_season(season_number)[episode_number - 1]

	def get_unaired(self):
		return [episode for episode in self
			if episode.is_unaired]

	def get_specials(self):
		return [episode for episode in self
			if episode.is_special]

# TODO Use __dict__ to set instance attributes
class EpisodeInfo(object):
	''''''
	def __init__(self, data):

		# print self.__dict__

		self.id = filter_node(data.id)
		self.episode_name = filter_node(data.episodename)
		self.combined_episode_number = filter_node(data.combined_episodenumber)
		self.combined_season = filter_node(data.combined_season)
		self.dvd_chapter = filter_node(data.dvd_chapter)
		self.dvd_disc_id = filter_node(data.dvd_discid)
		self.dvd_episode_number = filter_node(data.dvd_episodenumber)
		self.dvd_season = filter_node(data.dvd_season)
		self.director = filter_node(data.director)
		self.ep_img_flag = filter_node(data.epimgflag)
		self.episode_number = filter_node(data.episodenumber)
		self.first_aired = filter_node(data.firstaired)
		self.guest_stars = filter_node(data.gueststars)
		self.imdb_id = filter_node(data.imdb_id)
		self.language = filter_node(data.language)
		self.overview = filter_node(data.overview)
		self.production_code = filter_node(data.productioncode)
		self.rating = filter_node(data.rating)
		self.rating_count = filter_node(data.ratingcount)
		self.season_number = filter_node(data.seasonnumber)
		self.writer = filter_node(data.writer)
		self.absolute_number = filter_node(data.absolute_number)
		self.airs_after_season = filter_node(data.airsafter_season)
		self.airs_before_episode = filter_node(data.airsbefore_episode)
		self.airs_before_season = filter_node(data.airsbefore_season)
		self.filename = filter_node(data.filename)
		self.last_updated = filter_node(data.lastupdated)
		self.season_id = filter_node(data.seasonid)
		self.series_id = filter_node(data.seriesid)
		self.thumb_added = filter_node(data.thumb_added)
		self.thumb_width = filter_node(data.thumb_width)
		self.thumb_height = filter_node(data.thumb_height)
		
		# check if the episode was aired or not
		air_date = time.strptime(data.firstaired.string, '%Y-%m-%d')
		current_date = time.localtime(time.time())
		self.is_unaired = (current_date < air_date)
		
		# check if the episode is a special episode
		self.is_special = (self.season_number == '0')

		# print self.__dict__

class PyTVDB(object):
	''''''
	mirror = 'http://thetvdb.com'

	def __init__(self, api_key, language='en'):
		''''''
		self.api_key = api_key
		self.language = language

	# TODO Implement TypeArgumentException, IOException, BadZipFileException, HTTP404Exception, ConnectionException
	def _get_data(self, series_id):
		'''get series(tv show) information from thetvdb.com and cache the results'''

		series_id = str(series_id)

		response = requests.get('%s/api/%s/series/%s/all/%s.zip' % (self.mirror, self.api_key, series_id, self.language))
		if response.status_code != 200:
			return

		with TemporaryFile() as tmp_file:
			tmp_file.write(response.content)

			with ZipFile(tmp_file, 'r') as zip_file:
				data = {}

				with zip_file.open('%s.xml' % (self.language)) as xml_info:
					data['info'] = BeautifulSoup(xml_info.read())

				# with zip_file.open('actors.xml') as xml_actors:
				# 	data['actors'] = BeautifulSoup(xml_actors.read())

				# with zip_file.open('banners.xml') as xml_graphics:
				# 	data['graphics'] = BeautifulSoup(xml_graphics.read())

		return data

	# TODO raise ArgumentTypeError, ConnectionException, HTTPNot200CodeError
	def search(self, query):
		'''
		search thetvdb.com database for series(tvshow) containing the query 
		and return a list of SeriesPreview objects with the results
		'''

		response = requests.get('%s/api/GetSeries.php?seriesname=%s' % (self.mirror, query))
		response.raise_for_status()

		data = BeautifulSoup(response.text).find_all('series')

		if len(data) > 1:
			results = []

			for series in data:
				results.append(SeriesPreview(series))
		else :
			return

		return results

	def get_series(self, series_id) :
		'''get series(tv show) info from thetvdb.com and return a SeriesInfo object'''

		return SeriesInfo(self._get_data(series_id))

	# def get_actors(self, series_id):
	# 	pass

	# def get_actor(self, actor_id):
	# 	pass

	# # server_time 1399036356
	# def get_updates(self, server_time, *series_id):
	# 	pass

	# #TODO implement graphics request
	# def get_graphics(self, series_id):
	# 	pass

	# def get_banners(self, series_id):
	# 	pass

	# def get_posters(self, series_id):
	# 	pass

	# def get_fanart(self, series_id):
	# 	pass

	# def get_series_posters(self, series_id):
	# 	pass

	# def get_season_posters(self, series_id, season_number):
	# 	pass


#------------ TESTING
# series_id: ['game of thrones': 121361, 'breaking bad': 81189]

tvdb = PyTVDB('D229EEECFE78BA5F')

# search = tvdb.search('thrones')
# for s in search:
# 	print s.id, s.title

series = tvdb.get_series(121361)
# print series.episodes
# print series.episodes.get_season('2')

episodes = series.episodes

print '\n>>>> INCLUDE SPECIALS', episodes.include_specials, 'INCLUDE UNAIRED', episodes.include_unaired
print '\nEPISODES LEN:', len(episodes)
for ep in episodes:
	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

episodes.include_specials = True
episodes.include_unaired = False

print '\n>>>> INCLUDE SPECIALS', episodes.include_specials, 'INCLUDE UNAIRED', episodes.include_unaired
print '\nEPISODES LEN:', len(episodes)
for ep in episodes:
	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

episodes.include_specials = True
episodes.include_unaired = True

print '\n>>>> INCLUDE SPECIALS', episodes.include_specials, 'INCLUDE UNAIRED', episodes.include_unaired
print '\nEPISODES LEN:', len(episodes)
for ep in episodes:
	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

episodes.include_specials = False
episodes.include_unaired = True

print '\n>>>> INCLUDE SPECIALS', episodes.include_specials, 'INCLUDE UNAIRED', episodes.include_unaired
print '\nEPISODES LEN:', len(episodes)
for ep in episodes:
	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

print '\n>>>> GET SEASON 2'
season = series.episodes.get_season(2)
for ep in season:
	print ep.id, ep.season_number, ep.episode_number, ep.episode_name

print '\n>>>> GET SEASON 4'
season = series.episodes.get_season(4)
for ep in season:
	print ep.id, ep.season_number, ep.episode_number, ep.episode_name

print '\n>>>> SEASON 02 EPISODE 05'

s02e05 = series.episodes.get_episode(2, 5)
print s02e05.id, s02e05.season_number, s02e05.episode_number, s02e05.episode_name

# print '\n>>>> SEASON 05 EPISODE 01'

# s02e05 = series.episodes.get_episode(5, 1)
# print s02e05.id, s02e05.season_number, s02e05.episode_number, s02e05.episode_name

print '\n>>>> UNAIRED'
unaired = series.episodes.get_unaired()
for ep in unaired:
	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

print '\n>>>> SPECIALS'
specials = series.episodes.get_specials()
for ep in specials:
	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

# print tvdb.get_series(121361)
# print tvdb.get_series('121361')
# print tvdb.get_series('81189')
# print tvdb.get_series(81189)
# print tvdb.get_series('121361')
# print tvdb.get_series(90989999999999)

# episodes = tvdb.get_episodes(121361)
# for ep in episodes:
# 	print '%s - S%sE%s: %s' % (ep['first_aired'], ep['season_number'], ep['episode_number'], ep['episode_name'])

# season_episodes = tvdb.get_episodes_by_season(121361, 3)
# for ep in season_episodes:
# 	print '%s - S%sE%s: %s' % (ep['first_aired'], ep['season_number'], ep['episode_number'], ep['episode_name'])

