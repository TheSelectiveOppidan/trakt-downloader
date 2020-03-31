import requests
import json
import time
from datetime import datetime
from datetime import timedelta
from trakt_downloader import torrent_db
import os

cwd = os.getcwd()

client_id = ""
client_secret = ""

with open(cwd + "/trakt_credentials.json", 'r') as myfile:
    the_json = json.loads(myfile.read())
    client_id = the_json['client_id']
    client_secret = the_json['client_secret']

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

    except:
        print("Failed to find a torrent for " + str(name) + ' at ' + str(imdb_id))
        return ""

def trakt_id_from_obj(o):
    return o.trakt_id

def obtain_list_of_torrents_to_check():
    users = torrent_db.get_all_users()

    list_of_torrents = []

    disallowed_characters = [':', '/', '\\', '*', '?', '\"', '<', '>', '|']

    for user in users:
        watchlist_for_this_guy = get_watchlist_for(user.access_token)

        for movie in watchlist_for_this_guy:
            movie_name = movie['movie']['title']
            movie_year = movie['movie']['year']

            for char in disallowed_characters:
                movie_name = movie_name.replace(char, '')

            trakt_id = movie['movie']['ids']['slug']
            imdb_id = movie['movie']['ids']['imdb']

            if torrent_db.film_already_added(trakt_id) or trakt_id in map(trakt_id_from_obj, list_of_torrents):
                # print("Already has " + str(movie_name))
                continue

            torrent = get_torrent_link_for(imdb_id, movie_name)

            if torrent == "":
                continue

            this_torrent = TorrentToDownload(name=movie_name + " (" + str(movie_year) + ")", magnet_link=torrent, trakt_id=trakt_id)

            list_of_torrents.append(this_torrent)

        time.sleep(1)

    return list_of_torrents

def get_watchlist_for(access_token):
    try:
        watchlist = json.loads(requests.get('https://api.trakt.tv/users/me/watchlist/movies',
                                            headers={'trakt-api-key':client_id,
                                                     'Authorization': 'Bearer ' + str(access_token)})
                               .text)

        return watchlist
    except:
        print("Failed to get watchlist for user with token " + str(access_token))

def do_authorize_loop():
    try:
        response = json.loads(requests.post("https://api.trakt.tv/oauth/device/code",params={'client_id': client_id}).text)
        code = str(response['user_code'])
        device_code = str(response['device_code'])
        verification_link = str(response['verification_url'])
        polling_time = int(response['interval'])
        expires_in = int(response['expires_in'])

        authorized = False

        print("Please visit " + verification_link + " and enter code " + code)

        while not authorized and expires_in > 0:
            try:
                print("Checking if authorized")
                poll = requests.post('https://api.trakt.tv/oauth/device/token', params={
                    'code': device_code,
                    'client_id': client_id,
                    'client_secret': client_secret
                })

                if poll.status_code == 200:
                    json_response = json.loads(poll.text)

                    access_token = json_response['access_token']
                    refresh_token = json_response['refresh_token']
                    expires_at = datetime.now() + timedelta(seconds=json_response['expires_in'])

                    torrent_db.add_user(access_token, refresh_token, expires_at)

                    authorized = True

                    return True
            except:
                print("Something went wrong with the authorization. Please restart the program")
                return False

            expires_in -= polling_time
            time.sleep(polling_time)

        if not authorized and expires_in <= 0:
            print("Authorization timed out. Please try again")
            return False

    except Exception as e:
        print(e)
        print("Something went wrong authorizing")
