from deluge_client import DelugeRPCClient

from trakt_downloader import configuration, scraper, torrent_db, deluge_connection, trakt_connection

import time
from datetime import datetime

##NEED TO INSTALL
## pip install deluge-client
## pip install sqlalchemy

client = None

deluge_server_ip = None
deluge_server_port = None
deluge_username = None
deluge_password = None

live_config = None

def start():
    global client, deluge_password, deluge_server_ip, deluge_server_port, deluge_username, live_config

    if not configuration.check():
        print("Please fill in the configuration file I just created then rerun me.")
        exit()

    live_config = configuration.get_config()

    option = ""

    while option != 'n':
        option = input("Do you want to add a new account? (y/n)")

        if option == 'y':
            if not scraper.do_authorize_loop():
                option = ''

    deluge_server_ip = live_config['deluge_ip']
    deluge_server_port = int(live_config['deluge_port'])
    deluge_username = live_config['deluge_username']
    deluge_password = live_config['deluge_password']

    client = DelugeRPCClient(deluge_server_ip, deluge_server_port, deluge_username, deluge_password)

    try:
        client.connect()
    except Exception as e:
        print(e)

    print("is Connected to Deluge: " + str(client.connected))

    do_deluge_stuff()

def do_deluge_stuff():
    global client, live_config

    if not client.connected:
        print("Can't connect to the deluge server at " + str(deluge_server_ip) + ":" + str(
            deluge_server_port) + " with credentials (" + str(deluge_username) + "->" + str(deluge_password) + ")")
    else:
        check_interval = max(live_config['check_every_x_seconds'], 5)
        trakt_pull_time = max(live_config['check_trakt_every_x_seconds'], 60)
        current_trakt_pull_time = trakt_pull_time

        while True:
            try:
                if current_trakt_pull_time >= trakt_pull_time:
                    current_trakt_pull_time = 0
                    trakt_connection.pull_movies(client)

                print("Check at " + str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")) + " with " + str(
                    len(torrent_db.get_all_active())) + " active")

                deluge_connection.check_progress(client)
            except Exception as e:
                print(e)
                pass

            print("-----------")
            current_trakt_pull_time += check_interval
            time.sleep(check_interval)