# Trakt Puller - Download your watchlist instantly!
This repository contains the code for the script to check and download movies off of a users watchlist.

Features:
- Login to Trakt using their OAuth flow
- Connect to multiple trakt accounts to pull from different users watchlists.
- Check the watchlist of all users, find high quality torrents for the movies in their watchlist and initialise a download via a deluge server.
- Keep track of active downloads in the deluge server. Download control to make sure a movie isn't downloaded twice.
- When a download is completed, it can remove all the crappy files and keep the important files (the video and any subtitle files), and it renames the folder to a more user friendly name. (Only when the Deluge server and script have a common file system)
  
Planned features for the future:
- Connect to lists as well as watchlists with the ability to delete an item from a list when it is downloaded. Allowing a user to download the file without clogging their watchlist.
- Create a webserver within the script so that a companion app can be made to monitor the state of the script and configure the script.
	+ Configure accounts that the script checks. Add/Remove Users.
	+ Configure lists for the linked accounts, whether to delete on download or not.
- Work with TV shows too.
	
		
        
  
