import time
import requests
from zipfile import ZipFile
from tempfile import TemporaryFile
from bs4 import BeautifulSoup

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

	def __repr__(self):
		'''
		'''
		return '{SeriesPreview: %s}' % (self.__dict__)


class SeriesInfo(object):
	'''
	'''
	def __init__(self, data):
		'''
		'''
		self.__dict__.update(sanitize_returned_data(data['info'].find('series')))
		
		self.episodes = EpisodesList(data['info'].find_all('episode'))
		self.actors = ActorsList(data['actors'].find_all('actor'))
		self.graphics = GraphicsList(data['graphics'].find_all('banner'))

	def __repr__(self):
		'''
		'''
		return '{SeriesInfo: %s}' % (self.__dict__)


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
		
		if (data.firstaired.string is not None):
			air_date = time.strptime(self.first_aired, '%Y-%m-%d')
			current_date = time.localtime(time.time())
			self.is_unaired = (current_date < air_date)
		else:
		 	self.is_unaired = False
		
		self.is_special = (self.season_number == '0')

	def __repr__(self):
		'''
		'''
		return '{EpisodeInfo: %s}' % (self.__dict__)


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
		return '{ActorInfo: %s}' % (self.__dict__)


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
		return '{GraphicInfo: %s}' % (self.__dict__)


class PyTVDB(object):
	'''
	'''
	version = '0.0.1'
	mirror = 'http://thetvdb.com'

	def __init__(self, api_key, language = 'en'):
		'''
		'''
		self.api_key = api_key
		self.language = language

	# TODO raise TypeArgumentException, IOException, BadZipFileException, HTTP404Exception, ConnectionException
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
		else:
			return None

		return results

	def get_series(self, series_id) :
		'''
		get series(tv show) info from thetvdb.com and return a SeriesInfo object
		'''
		return SeriesInfo(self._get_data(series_id))
