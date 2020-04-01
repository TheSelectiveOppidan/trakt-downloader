from trakt_downloader import scraper, torrent_db, trakt_credentials
import time
import json
import requests
import os
from datetime import timedelta

from trakt_downloader.scraper import get_torrent_link_for, TorrentToDownload

cwd = os.getcwd()

from trakt_downloader import torrent_db
from trakt_downloader.torrent_db import *

from trakt_downloader.deluge_connection import add_torrent_magnet

client_id = trakt_credentials.client_id
client_secret = trakt_credentials.client_secret

# with open(cwd + "/trakt_credentials.json", 'r') as myfile:
#     the_json = json.loads(myfile.read())
#     client_id = the_json['client_id']
#     client_secret = the_json['client_secret']

def trakt_id_from_obj(o):
    return o.trakt_id

def obtain_list_of_torrents_to_check():
    users = torrent_db.get_all_users()

    list_of_torrents = []

    disallowed_characters = [':', '/', '\\', '*', '?', '\"', '<', '>', '|']

    for user in users:
        watchlist_for_this_guy = get_watchlist_for(user)

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

def make_refresh_request(user):
    try:
        response = requests.post('https://api.trakt.tv/oauth/token',
                                json={
                                    'refresh_token':user.refresh_token,
                                    'client_id':client_id,
                                    'client_secret':client_secret,
                                    'grant_type':'refresh_token'
                                })

        if response.status_code == 401:
            print("User " + str(user.id) + " has invalid tokens. Going to remove them. Please reconnect.")
            torrent_db.remove_user(user)
        else:
            response_json = json.loads(response.text)

            new_access_token = response_json['access_token']
            new_refresh_token = response_json['refresh_token']
            new_expires_at = datetime.now() + timedelta(seconds=response_json['expires_in'])

            user.access_token = new_access_token
            user.refresh_token = new_refresh_token
            user.expires_at = new_expires_at

            new_user = TraktUser(id=user.id, access_token=new_access_token, refresh_token=new_refresh_token, expires_at=new_expires_at)

            torrent_db.update_user(new_user)
            print("Successfully refreshed")
    except:
        print("Something went wrong making a refresh attempt.")

def get_watchlist_for(user):
    try:
        response = requests.get('https://api.trakt.tv/users/me/watchlist/movies',
                                            headers={'trakt-api-key':client_id,
                                                     'Authorization': 'Bearer ' + str(user.access_token)})

        if response.status_code == 401:
            print("Refreshing access with " + str(user.refresh_token))
            make_refresh_request(user)
            return []
        else:
            watchlist = json.loads(response.text)
            return watchlist
    except:
        print("Failed to get watchlist for user with token " + str(user.access_token))
        return []

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

                    print("Successfully authorized user")
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