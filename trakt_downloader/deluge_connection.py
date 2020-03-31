from trakt_downloader import torrent_db
import os

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
                        print("rename mp4 file " + str(filename))
                        os.rename(destination + "/" + filename, destination_folder + "/" + torr.name + ".mp4")
                    elif (filename.endswith('.mkv')):
                        print("rename mkv file " + str(filename))
                        os.rename(destination + "/" + filename, destination_folder + "/" + torr.name + ".mkv")
                    else:
                        print("delete file " + str(filename))
                        os.remove(destination + "/" + filename)
                except:
                    pass

            os.renames(destination_folder, destination + "/" + torr.name)
        except:
            pass