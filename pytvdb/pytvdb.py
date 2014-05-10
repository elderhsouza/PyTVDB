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

def filter_dict_value(value):
	'''
	'''
	if '.jpg' in value:
		return '%s/banners/%s' % (PyTVDB.mirror, value)

	return value.encode('utf-8')

def filter_dict_key(key):
	'''
	'''
	search_for = (
		'seriesid', 'seriesname', 'firstaired', 'airs_dayofweek', 'contentrating', 'networkid',
		'ratingcount', 'addedby', 'lastupdated', 'combined_episodenumber', 'dvd_discid', 'dvd_episodenumber',
		'epimgflag', 'episodename', 'episodenumber', 'gueststars', 'productioncode', 'seasonnumber',
		'airsafter_season', 'airsbefore_episode', 'airsbefore_season', 'seasonid', 'sortorder',
		'bannerpath', 'bannertype', 'bannertype2', 'thumbnailpath', 'vignettepath'
	)
	replace_by = (
		'series_id', 'series_name', 'first_aired', 'airs_day_of_week', 'content_rating', 'network_id',
		'rating_count', 'added_by', 'last_updated', 'combined_episode_number', 'dvd_disc_id', 'dvd_episode_number',
		'ep_img_flag', 'episode_name', 'episode_number', 'guest_stars', 'production_code', 'season_number',
		'airs_after_season', 'airs_before_episode', 'airsbefore_season', 'season_id', 'sort_order',
		'banner_path', 'banner_type', 'banner_type_2', 'thumbnail_path', 'vignette_path'
	)
	if key in search_for:
		return replace_by[search_for.index(key)]
	
	return key

def sanitize_returned_data(data):
	'''
	'''
	result = {}
	for item in data:
		if item.name is not None and item.string is not None:
			result[filter_dict_key(item.name)] = filter_dict_value(item.string)

	return result


class SeriesPreview(object):
	'''
	'''
	def __init__(self, data):
		'''
		'''
		self.__dict__.update(sanitize_returned_data(data))


class SeriesInfo(object):
	'''
	'''
	def __init__(self, data):
		'''
		'''
		self.__dict__.update(sanitize_returned_data(data['info'].find('series')))
		#
		self.episodes = EpisodesList(data['info'].find_all('episode'))
		self.actors = ActorsList(data['actors'].find_all('actor'))
		self.graphics = GraphicsList(data['graphics'].find_all('banner'))


class EpisodesList(list):
	'''
	'''
	def __init__(self, episodes):
		'''
		'''
		self.include_unaired = False
		self.include_specials = False

		total_episodes = 0

		for episode in episodes:
			self.append(EpisodeInfo(episode))
			total_episodes += 1

		self.total_episodes = total_episodes

	def __iter__(self):
		'''
		'''
		return (self[i] for i in self._episodes_generator())

	def __len__(self):
		'''
		'''
 		return len(list(self._episodes_generator()))

	def _episodes_generator(self):
		'''
		'''
		i = 0
		while i < self.total_episodes:
			if (self.include_unaired or not self[i].is_unaired) and \
			(self.include_specials or not self[i].is_special):
				yield i
			i += 1

	# TODO raise IndexError, TypeError
	def get_season(self, season_number = 1):
		'''
		Gets all episodes from a specified season.

		Args:
		    season_number: the number of the season; defaults to 1
		Returns:
		    a list of EpisodeInfo objects for each episode on the season.
		Raises:
		    KeyError: if season_number is < 1 or > then the total number of seasons.
		    TypeError: if season_number is not convertible to an integer
		'''
		return [episode for episode in self
			if episode.season_number == str(season_number)]

	# TODO raise IndexError, TypeError
	def get_episode(self, season_number = 1, episode_number = 1):
		'''
		Get an episode from a specified season and episode number

		Args:
			season_number: the number of the season; defaults to 1
			episode_number: the number of the episode; defaults to 1
		Returns:
			an EpisodeInfo object or None if the episode is not found
		Raises:
			KeyError: if season_number or episode_number is < 1 or > then the total number of seasons and episodes
			TypeError: if season_number or episode_number is not convertible to an integer
		'''
		return self.get_season(season_number)[episode_number - 1]

	def get_unaired(self):
		'''
		returns a list with unaired espisodes
		'''
		return [self[i] for i in range(self.total_episodes)
			if self[i].is_unaired]

	def get_specials(self):
		'''
		returns a list with special objects (not conatined in any season)
		'''
		return [self[i] for i in range(self.total_episodes)
			if self[i].is_special]


class EpisodeInfo(object):
	'''
	'''
	def __init__(self, data):
		'''
		'''
		self.__dict__.update(sanitize_returned_data(data))
		
		# check if the episode was aired
		if (data.firstaired.string is not None):
			air_date = time.strptime(self.first_aired, '%Y-%m-%d')
			current_date = time.localtime(time.time())
			self.is_unaired = (current_date < air_date)
		else:
		 	self.is_unaired = False
		
		# check if the episode is a special
		self.is_special = (self.season_number == '0')

	def __repr__(self):
		'''
		'''
		return '{EpisodeInfo: {id: %s, season: %s, episode number: %s, episode name: %s}}' % \
			(self.id, self.season_number, self.episode_number, self.episode_name)


class ActorsList(list):
	'''
	'''
	def __init__(self, actors):
		'''
		'''
		for actor in actors:
			self.append(ActorInfo(actor))


class ActorInfo(object):
	'''
	'''
	def __init__(self, data):
		'''
		'''
		self.__dict__.update(sanitize_returned_data(data))

	def __repr__(self):
		'''
		'''
		return '{ActorInfo: {id:%s, name: %s, role: %s}}' % \
			(self.id, self.name, self.role)


class GraphicsList(list):
	'''
	'''
	TYPE_FANART = 'fanart'
	TYPE_POSTER = 'poster'
	TYPE_SEASON = 'season'
	TYPE_SERIES = 'series'

	def __init__(self, graphics):
		'''
		'''
		for graphic in graphics:
			self.append(GraphicInfo(graphic))

	def get_by_type(self, image_type):
		'''
		'''
		return [graphic for graphic in self if graphic.banner_type == image_type]


class GraphicInfo(object):
	'''
	'''
	def __init__(self, data):
		'''
		'''
		self.__dict__.update(sanitize_returned_data(data))

	def __repr__(self):
		'''
		'''
		return '{GraphicInfo: {id: %s, type: %s, path: %s}}\n' % \
			(self.id, self.banner_type, self.banner_path)
		# return '%s\n' % (self.__dict__)


class PyTVDB(object):
	'''
	'''
	mirror = 'http://thetvdb.com'

	def __init__(self, api_key, language = 'en'):
		'''
		'''
		self.api_key = api_key
		self.language = language

	# TODO Implement TypeArgumentException, IOException, BadZipFileException, HTTP404Exception, ConnectionException
	def _get_data(self, series_id):
		'''
		get series(tv show) information from thetvdb.com and cache the results
		'''
		series_id = str(series_id)

		response = requests.get('%s/api/%s/series/%s/all/%s.zip' % (self.mirror, self.api_key, series_id, self.language))
		if response.status_code != 200:
			return None

		with TemporaryFile() as tmp_file:
			tmp_file.write(response.content)

			with ZipFile(tmp_file, 'r') as zip_file:
				data = {}

				with zip_file.open('%s.xml' % (self.language)) as xml_info:
					data['info'] = BeautifulSoup(xml_info.read())

				with zip_file.open('actors.xml') as xml_actors:
				 	data['actors'] = BeautifulSoup(xml_actors.read())

				with zip_file.open('banners.xml') as xml_graphics:
				 	data['graphics'] = BeautifulSoup(xml_graphics.read())

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

			for series_data in data:
				results.append(SeriesPreview(series_data))
		else :
			return None

		return results

	def get_series(self, series_id) :
		'''
		get series(tv show) info from thetvdb.com and return a SeriesInfo object
		'''
		return SeriesInfo(self._get_data(series_id))


#------------ TESTING
# series_id: ['game of thrones': 121361, 'breaking bad': 81189]

tvdb = PyTVDB('D229EEECFE78BA5F')

# search = tvdb.search('thrones')
# for s in search:
# 	print(s.id, s.title, s.overview)

series = tvdb.get_series(121361)

# actors = series.actors
# print(actors)

graphics = series.graphics
# print(graphics)

posters = graphics.get_by_type(GraphicsList.TYPE_POSTER)
print posters

# episodes = series.episodes
# print '\n>>>> INCLUDE SPECIALS', episodes.include_specials, 'INCLUDE UNAIRED', episodes.include_unaired
# print '\nEPISODES LEN:', len(episodes)
# for ep in episodes:
# 	print ep

# episodes.include_specials = True
# episodes.include_unaired = True
# print '\n>>>> INCLUDE SPECIALS', episodes.include_specials, 'INCLUDE UNAIRED', episodes.include_unaired
# print '\nEPISODES LEN:', len(episodes)
# for ep in episodes:
# 	print ep

# episodes.include_specials = False
# episodes.include_unaired = True
# print '\n>>>> INCLUDE SPECIALS', episodes.include_specials, 'INCLUDE UNAIRED', episodes.include_unaired
# print '\nEPISODES LEN:', len(episodes)
# for ep in episodes:
# 	print ep

# episodes.include_specials = True
# episodes.include_unaired = False
# print '\n>>>> INCLUDE SPECIALS', episodes.include_specials, 'INCLUDE UNAIRED', episodes.include_unaired
# print '\nEPISODES LEN:', len(episodes)
# for ep in episodes:
# 	print ep

# print '\n>>>> GET SEASON 2'
# season = series.episodes.get_season(2)
# for ep in season:
# 	print ep

# print '\n>>>> GET SEASON 4'
# season = series.episodes.get_season(4)
# for ep in season:
# 	print ep.id, ep.season_number, ep.episode_number, ep.episode_name

# episodes.include_unaired = False
# print '\n>>>> GET SEASON 4', 'include_unaired', episodes.include_unaired
# season = series.episodes.get_season(4)
# for ep in season:
# 	print ep.id, ep.season_number, ep.episode_number, ep.episode_name

# print '\n>>>> SEASON 02 EPISODE 05'

# got_s02e05 = series.episodes.get_episode(2, 5)
# print got_s02e05.id, got_s02e05.season_number, got_s02e05.episode_number, got_s02e05.episode_name

# # print '\n>>>> SEASON 05 EPISODE 01'

# # got_s02e05 = series.episodes.get_episode(5, 1)
# # print got_s02e05.id, got_s02e05.season_number, got_s02e05.episode_number, got_s02e05.episode_name

# episodes.include_unaired = True

# print '\n>>>> GET UNAIRED', episodes.include_unaired
# unaired = episodes.get_unaired()
# for ep in unaired:
# 	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

# episodes.include_unaired = False

# print '\n>>>> GET UNAIRED', episodes.include_unaired
# unaired = episodes.get_unaired()
# for ep in unaired:
# 	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

# episodes.include_specials = True
# print '\n>>>> GET SPECIALS', episodes.include_specials
# specials = episodes.get_specials()
# for ep in specials:
# 	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

# episodes.include_specials = False

# print '\n>>>> GET SPECIALS', episodes.include_specials
# specials = episodes.get_specials()
# for ep in specials:
# 	print ep.id, ep.season_number, ep.episode_number, ep.episode_name, ep.is_special,  ep.is_unaired

# print '\n>>>> CONTAINS: G.O.T EPISODE IN G.O.T EPISODES LIST', got_s02e05, episodes
# print (got_s02e05 in episodes)

# bb = tvdb.get_series(81189)
# bb_episodes = bb.episodes
# bb_s04e05 = bb.episodes.get_episode(4, 5)

# print '\n>>>> CONTAINS: B.B EPISODE IN B.B EPISODES LIST', bb_s04e05, bb_episodes
# print (bb_s04e05 in bb_episodes)

# print '\n>>>> CONTAINS: G.O.T EPISODE IN B.B EPISODES LIST', got_s02e05, bb_episodes
# print (got_s02e05 in bb_episodes)

# print '\n>>>> CONTAINS: B.B EPISODE IN G.O.T EPISODES LIST', bb_s04e05, episodes
# print (bb_s04e05 in episodes)

# # print tvdb.get_series(121361)
# # print tvdb.get_series('121361')
# # print tvdb.get_series('81189')
# # print tvdb.get_series(81189)
# # print tvdb.get_series('121361')
# # print tvdb.get_series(90989999999999)

