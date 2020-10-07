from trakt_downloader import popcorn_interface, torrent_db, trakt_credentials
import time
import json
import requests
import os
from datetime import timedelta
from datetime import datetime

from trakt_downloader.popcorn_interface import get_torrent_link_for, TorrentToDownload

cwd = os.getcwd()

from trakt_downloader import torrent_db
from trakt_downloader.torrent_db import *

from trakt_downloader.deluge_connection import add_torrent_magnet

##NOTE FOR DEVELOPMENT
##CREATE A FILE CALLED trakt_credentials.py which just has the 2 variables we access here as Strings.
##Have fun
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
        watchlist_for_this_guy.extend(get_wantlist_for(user))

        for movie in watchlist_for_this_guy:
            movie_name = movie['movie']['title']
            movie_year = movie['movie']['year']

            for char in disallowed_characters:
                movie_name = movie_name.replace(char, '')

            trakt_id = movie['movie']['ids']['slug']
            imdb_id = movie['movie']['ids']['imdb']

            if torrent_db.film_already_added(trakt_id) or trakt_id in map(trakt_id_from_obj, list_of_torrents):
                # print("Already has " + str(movie_name))
                delete_from_wantlist(trakt_id)
                continue

            torrent = get_torrent_link_for(imdb_id, movie_name)

            if torrent == "":
                continue

            this_torrent = TorrentToDownload(name=movie_name + " (" + str(movie_year) + ")", magnet_link=torrent,
                                             trakt_id=trakt_id)

            list_of_torrents.append(this_torrent)

        time.sleep(1)

    return list_of_torrents


def make_refresh_request(user):
    try:
        response = requests.post('https://api.trakt.tv/oauth/token',
                                 json={
                                     'refresh_token': user.refresh_token,
                                     'client_id': client_id,
                                     'client_secret': client_secret,
                                     'grant_type': 'refresh_token'
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

            new_user = TraktUser(id=user.id, access_token=new_access_token, refresh_token=new_refresh_token,
                                 expires_at=new_expires_at)

            torrent_db.update_user(new_user)
            print("Successfully refreshed")
    except:
        print("Something went wrong making a refresh attempt.")


def do_refresh_for(user):
    print("Refreshing access with " + str(user.refresh_token))
    make_refresh_request(user)


def get_watchlist_for(user):
    try:
        response = requests.get('https://api.trakt.tv/users/me/watchlist/movies',
                                headers={'trakt-api-key': client_id,
                                         'Authorization': 'Bearer ' + str(user.access_token)})

        if response.status_code == 401:
            do_refresh_for(user)
            return []
        else:
            watchlist = json.loads(response.text)
            return watchlist
    except:
        print("Failed to get watchlist for user with token " + str(user.access_token))
        return []


def get_user_wantlist(user):
    try:
        lists_response = requests.get("https://api.trakt.tv/users/me/lists",
                                      headers={'trakt-api-key': client_id,
                                               'Authorization': 'Bearer ' + str(user.access_token)})
        if lists_response.status_code == 401:
            do_refresh_for(user)
            return None
        else:
            lists = json.loads(lists_response.text)
            wantlist = next((x for x in lists if str(x['name']).lower() == "wantlist"), None)
            return wantlist

    except Exception as e:
        print("Failed getting user wantlist " + str(e))
        return None


def get_wantlist_for(user):
    try:
        wantlist = get_user_wantlist(user)

        if wantlist != None:
            if wantlist['item_count'] > 0:
                wantlist_id = wantlist['ids']['trakt']
                list_items_response = requests.get(
                    "https://api.trakt.tv/users/me/lists/" + str(wantlist_id) + "/items/movies",
                    headers={'trakt-api-key': client_id,
                             'Authorization': 'Bearer ' + str(user.access_token)})

                if list_items_response.status_code == 401:
                    do_refresh_for(user)
                else:
                    items = json.loads(list_items_response.text)

                    items_to_return = []

                    for item in items:
                        items_to_return.append(item)

                    return items_to_return

        return []
    except Exception as e:
        print(e)
        print("Failed to get wantlist for user with token " + str(user.access_token))
        return []


def push_all_to_collection():
    for torr in torrent_db.get_all_complete():
        added_at = time.time()

        if (torr.time_added != None):
            added_at = torr.time_added

        mark_collected(torr.trakt_id, datetime.utcfromtimestamp(added_at))


def remove_all_from_wantlist():
    for torr in torrent_db.get_all_complete():
        delete_from_wantlist(torr.trakt_id)


def mark_collected(trakt_id, date, alreadyRefreshed=False):
    users = torrent_db.get_all_users()

    for user in users:
        try:
            response = requests.post('https://api.trakt.tv/sync/collection',
                                     headers={'trakt-api-key': client_id,
                                              'Authorization': 'Bearer ' + str(user.access_token),
                                              'Content-Type': 'application/json'
                                                },
                                     json={
                                         "movies": [
                                             {
                                                 "media_type": "digital",
                                                 "collected_at": str(date.strftime("%Y-%m-%dT%H:%M:%S")),
                                                 "ids": {"slug": trakt_id}
                                             }
                                         ]
                                     }
                                     )

            if response.status_code == 401:
                if not alreadyRefreshed:
                    do_refresh_for(user)
                    mark_collected(trakt_id, date, True)
            else:
                json_response = json.loads(response.text)
                if json_response['added']['movies'] > 0:
                    print("collected " + str(trakt_id) + " in trakt")

                if len(json_response['not_found']['movies']) > 0:
                    print("failed to collect " + str(trakt_id) + " on trakt")
        except Exception as e:
            print("Failed add to collection request for " + str(user.access_token))


def delete_from_wantlist(trakt_id, alreadyRefreshed=False):
    users = torrent_db.get_all_users()

    for user in users:
        try:
            wantlist = get_user_wantlist(user)

            if wantlist != None:
                wantlist_id = wantlist['ids']['trakt']

                response = requests.post('https://api.trakt.tv/users/me/lists/' + str(wantlist_id) + '/items/remove',
                                         headers={'trakt-api-key': client_id,
                                                  'Authorization': 'Bearer ' + str(user.access_token)},
                                         json={
                                             "movies":[
                                                 {
                                                     "ids": { "slug": trakt_id }
                                                 }
                                             ]
                                         }
                                         )

                if response.status_code == 401:
                    if not alreadyRefreshed:
                        do_refresh_for(user)
                        delete_from_wantlist(trakt_id, True)
                else:
                    json_response = json.loads(response.text)
                    if json_response['deleted']['movies'] > 0:
                        print("deleted " + str(trakt_id) + " from wantlist")

                    if len(json_response['not_found']['movies']) > 0:
                        print("failed to delete " + str(trakt_id) + " from wantlist")

        except Exception as e:
            print("Failed delete from wantlist request for " + str(user.access_token))


def do_authorize_loop():
    try:
        response = json.loads(
            requests.post("https://api.trakt.tv/oauth/device/code", params={'client_id': client_id}).text)
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
