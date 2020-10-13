import json

import requests

from trakt_downloader.deluge_connection import add_torrent_magnet

movies_url = "https://movies-v2.api-fetch.sh"
shows_url = "https://tv-v2.api-fetch.sh"

class TorrentToDownload:
    name = ""
    magnet_link = ""
    trakt_id= ""

    def __init__(self, name, magnet_link, trakt_id):
        self.name = name
        self.magnet_link = magnet_link
        self.trakt_id = trakt_id

    def __str__(self):
        return str(self.name) + " (" + str(self.trakt_id) + ") from " + str(self.magnet_link)

def get_torrent_link_for(imdb_id, name):
    global movies_url, shows_url
    try:
        popcorn_post = json.loads(requests.get(str(movies_url) + '/movie/' + str(imdb_id)).text)
        torrents = popcorn_post['torrents']['en']

        if '2160p' in torrents.keys():
            return torrents['2160p']['url']
        if '1080p' in torrents.keys():
            return torrents['1080p']['url']
        elif '720p' in torrents.keys():
            return torrents['720p']['url']
        else:
            print("Can't find 2160p, 1080p OR 720p source for " + str(name) + " at " + str(imdb_id))
            return ""

    except Exception as e:
        # print(e)
        print("Failed to find a torrent for " + str(name) + ' at ' + str(imdb_id))
        return ""

def get_show_info(imdb_id):
    global movies_url, shows_url
    try:
        popcorn_post = json.loads(requests.get(str(shows_url) + '/show/' + str(imdb_id)).text)

        seasons = {}

        for episode in popcorn_post['episodes']:
            if episode['season'] not in seasons.keys():
                seasons[episode['season']] = {}

            seasons[episode['season']][episode['episode']] = episode

        print("found " + str(len(seasons.keys())) + " seasons")

        for season in seasons.keys():
            print("season " + str(season) + " has " + len(seasons[season]) + " episodes")



    except Exception as e:
        # print(e)
        print("Failed to find a torrent for " + str(imdb_id) + ' at ' + str(imdb_id))
        return ""


def pull_movies(client, CONNECT_TO_DELUGE=True):
    print("FETCHING FROM TRAKT")

    from trakt_downloader import trakt_connection
    list_of_torrents = trakt_connection.obtain_list_of_torrents_to_check()

    if CONNECT_TO_DELUGE:
        for torrent in list_of_torrents:
            add_torrent_magnet(client, torrent)


get_show_info("tt2930604")