import json

import requests

from trakt_downloader.deluge_connection import add_torrent_magnet

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
    try:
        popcorn_post = json.loads(requests.get('https://tv-v2.api-fetch.website/movie/' + str(imdb_id)).text)
        torrents = popcorn_post['torrents']['en']

        if '1080p' in torrents.keys():
            return torrents['1080p']['url']
        elif '720p' in torrents.keys():
            return torrents['720p']['url']
        else:
            print("Can't find 1080p OR 720p source for " + str(name) + " at " + str(imdb_id))
            return ""

    except Exception as e:
        print(e)
        print("Failed to find a torrent for " + str(name) + ' at ' + str(imdb_id))
        return ""

def pull_movies(client):
    print("FETCHING FROM TRAKT")

    from trakt_downloader import trakt_connection
    list_of_torrents = trakt_connection.obtain_list_of_torrents_to_check()

    for torrent in list_of_torrents:
        add_torrent_magnet(client, torrent)
