import os
import json
from trakt_downloader import torrent_db
import uuid
import time

cwd = os.path.dirname(os.path.abspath(__file__))
config_file_path = cwd + "/config.json"

default_config = {}

#Ip for the deluge server
default_config['deluge_ip'] = '127.0.0.1'

# Port for the deluge server
default_config['deluge_port'] = '58846'

# Username for the deluge server
default_config['deluge_username'] = 'localclient'

#Password for the deluge server
default_config['deluge_password'] = 'deluge'

#Progress check interval in seconds
default_config['check_every_x_seconds'] = 5

# This is best as a multiple of the one above, and has to be bigger than the above one.
# If it is less than the one above, it will happen at the same interval as the progress check
default_config['check_trakt_every_x_seconds'] = 60

#######################
# This method checks to see if a configuration file exists.
# if not, it creates a new one and the main app will
# instruct the user to fill it in and rerun the script
#
# returns Boolean - True if config already exists, False if not
########################
def check(start_dir = cwd):
    config_file_path = start_dir + "/config.json"
    torrent_db.set_config_item("install_id", str(uuid.uuid4()))
    torrent_db.set_config_item("install_date", str(time.time()))

    if not os.path.isfile(config_file_path):
        with open(config_file_path, 'w') as output:
            json.dump(default_config, output, indent=4)
            return False
    else:
        return True


######################
# This method fetches the configuration from the defined
# config file and returns it as a dict
#
# returns Dictionary containing the configuration file contents
######################
def get_config(start_dir = cwd):
    config_file_path = start_dir + "/config.json"
    with open(config_file_path) as config_file:
        return json.load(config_file)
