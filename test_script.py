import praw, urllib, json, time, re

#goddesses

#imgur api https://api.imgur.com/oauth2
#praw api http://praw.readthedocs.io/en/stable/index.html#main-page

def get_pics_by_subreddit(subreddit, limit):
	user_agent = "windows:testing_agent:0.1 (by /u/Domuska)"
	reddit = praw.Reddit(user_agent = user_agent)
	thing_limit = limit
	
	#get submissions
	submissions = reddit.get_subreddit(subreddit).get_hot(limit=thing_limit)
	
	filename = "user_1" + time.strftime("%d/%m/%Y")
	#variable that is used in file names
	variable = 1
	#print submission urls
	
	for submission in submissions:
		print ("\n")
		print(submission.url)
		url = submission.url
		filename = str(submission.author) + "-" + time.strftime("%Y_%m_%d_%I_%M")
		
		#handle imgur separate from other image sources, imgur can have 
		#albums and all that jazz
		
		if "imgur" in url:
			if "/a/" in url or "gallery" in url:
				print ("seems we gots an album")
				album_variable = 1
				#handle imgur endpoint stuff
				album_data = handle_imgur_album(url)
				#how many elements in the data
				#len (album_data)
				#todo: handle non-static images in albums,
				for album in album_data:
					album_img_url = album['link']
					urllib.request.urlretrieve(album_img_url, filename +  "_" + str(album_variable) + ".jpg")
					album_variable += 1
				
			#convert imgur links to pure picture links			
			#todo: handle non-static images
			else:
				if "i.imgur" not in url:
					url = url + ".jpg"
				
				urllib.request.urlretrieve(url, filename + ".jpg")
		
		elif "reddituploads" in url:
			#print("saving url " + url + " as image " + filename + ".jpg")
			urllib.request.urlretrieve(url, filename + ".jpg")
		
		variable += 1
			
			
#helper method to handle an imgur album
#as parameter takes the ID of the album
#returns: dictionary that has the info that album API returns			
def handle_imgur_album(album_url):

	#get the point where album url starts, using re and a regex
	regex = re.search('/a/', album_url)
	#splice the id from the whole url
	album_id = album_url[regex.end():]
	
	#use the album api to get urls to the individual images
	gallery_endpoint_url = "https://api.imgur.com/3/album/" + album_id + "/images"
	#add my own client-id to the request as header
	header = {'Authorization' : 'Client-ID INSERT_KEY_HERE_AND_CLOSE_THE_STRING }
	request = urllib.request.Request(gallery_endpoint_url, None, header)
	#get the response
	response = urllib.request.urlopen(request)
	
	#decode the response with utf-8 (hopefully correct)
	response_str = response.read()
	response_str = response_str.decode('utf-8')
	#print(response_str)
	
	data = json.loads(response_str)
	#return only the 'data' portion
	return data['data']
	
	
	
	