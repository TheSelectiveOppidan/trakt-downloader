# Trakt Puller - Download your watchlist instantly!
This repository contains the code for the script to check and download movies off of a users watchlist.

Current Version: v0.7

Features:
- Login to Trakt using their OAuth flow, refreshes token when it expires
- Connect to multiple trakt accounts to pull from different users watchlists.
- Check the watchlist of all users, find high quality torrents for the movies in their watchlist and initialise a download via a deluge server.
- Keep track of active downloads in the deluge server. Download control to make sure a movie isn't downloaded twice.
- When a download is completed, it can remove all the crappy files and keep the important files (the video and any subtitle files), and it renames the folder to a more user friendly name. (Only when the Deluge server and script have a common file system)
- If the user creates a Trakt list called `Wantlist` then this script will add the downloads as usual and then once the film is downloaded, delete it from the wantlist to avoid clogging watchlists.
- When a film is downloaded (or has been, checks local db) that movie is added to your Trakt collection, so you can see when something has been successfully downloaded. 
  
Planned features for the future:

- Create a webserver within the script so that a companion app can be made to monitor the state of the script and configure the script.
	+ Configure accounts that the script checks. Add/Remove Users.
	+ Configure lists for the linked accounts, whether to delete on download or not.
- Work with TV shows too.
	
		
        
  
