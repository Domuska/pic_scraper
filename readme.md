Script for gathering URLS from a subreddit and downloading the pictures submissions to that subreddit contains. Can handle different image providers.

Usage:
	-install python 3.x
	-request your own client ID at https://api.imgur.com/oauth2, use it in the test script
	-in future might need to get your own client ID for gfycat at https://developers.gfycat.com/api/
	-run python
	-run virtual environment:
		-for example: C:\development\pic_scraper\venv\Scripts\activate
		-for deactivating: C:\development\pic_scraper\venv\Scripts\deactivate
	OR
	-install praw through PIP: pip install praw

	After this, use either the GUI or command line
	
	GUI is started with, assuming you have python in your path and are in the folder with the script:
	python reddit_scraper.py
	
	Command line:
	
	import reddit_scraper as r
	r.get_pics_by_subreddit('pics', 20)
	
	-the script should download the pictures to the path provided in the script, folder might need to be already made when the script is ran
	
	-you can also use it to download pictures with only imgur URL, use function download_from_imgur()
		-1st parameter is URL as a string
		-2nd parameter is the file in your file path as a string, folder dividers in Python style as / rather than \ as is done on Windows. Don't forget the trailing /
		
	