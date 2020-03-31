from trakt_downloader import scraper, torrent_db
import time

def add_torrent_magnet(client, torrent):
    id = client.call('core.add_torrent_magnet', torrent.magnet_link, [])
    if (id is None):
        # print("Already have " + str(torrent.name))
        id = str(time.time())
        torrent_db.add_to_db(id, torrent)
        torrent_db.set_finished(id, 1)
        return

    id = id.decode()

    if (id != "None"):
        torrent_db.add_to_db(id, torrent)
        # torrent_db.set_finished(id, True)

def pull_movies(client):
    print("FETCHING FROM TRAKT")

    list_of_torrents = scraper.obtain_list_of_torrents_to_check()

    for torrent in list_of_torrents:
        add_torrent_magnet(client, torrent)
