Script for gathering URLS from a subreddit and downloading the pictures submissions to that subreddit contains. Can handle different image providers.

Usage:
	-install python 3.x
	-install praw through PIP: pip install praw (see test script for URL to imgur api, instructions there)
	-request your own client ID at https://api.imgur.com/oauth2, use it in the test script
	-in future might need to get your own client ID for gfycat at https://developers.gfycat.com/api/
	-run python
	
	import test_script as r
	r.get_pics_by_subreddit('pics', 20)
	
	-the script should download the pictures to the path provided in the script, folder might need to be already made when the script is ran
	
	