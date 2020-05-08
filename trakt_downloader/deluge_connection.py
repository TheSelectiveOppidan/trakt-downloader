from trakt_downloader import torrent_db
import os
import time

def check_progress(client):
    check = client.call("core.get_torrents_status", {}, [])

    for torr in torrent_db.get_all_active():
        # print(str(torr.name) + " is still awaiting being finished")

        encoded_id = torr.id.encode('utf-8')
        this_item = None

        try:
            this_item = check[encoded_id]
        except KeyError as key:
            print("Can't find an update for " + str(torr.name))
            continue

        torrent_db.update_with_live_data(torr, this_item)

        film_name = this_item[b'name'].decode()

        completed = this_item[b'is_finished']

        if not completed:
            continue

        torrent_db.set_finished(torr.id, 1)

        destination = this_item[b'move_completed_path'].decode()
        destination_folder = destination + '/' + this_item[b'name'].decode()

        try:
            for file in check[encoded_id][b'files']:
                filename = file[b'path'].decode()

                try:
                    if (filename.endswith('.mp4')):
                        os.rename(destination + "/" + filename, destination_folder + "/" + torr.name + ".mp4")
                        print("rename mp4 file " + str(filename))
                    elif (filename.endswith('.mkv')):
                        os.rename(destination + "/" + filename, destination_folder + "/" + torr.name + ".mkv")
                        print("rename mkv file " + str(filename))
                    elif (filename.endswith('.srt')):
                        print("leaving subtitle file " + str(filename))
                    else:
                        os.remove(destination + "/" + filename)
                        print("delete file " + str(filename))
                except Exception as e:
                    print("Unable to modify results. Is this script running on the same system as the deluge server?")
                    print(e)
                    pass

            os.renames(destination_folder, destination + "/" + torr.name)
        except Exception as e:
            print("Unable to rename directory. Is this script running on the same system as the deluge server?")
            print(e)
            pass

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