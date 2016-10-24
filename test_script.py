import praw, urllib, json, time, re
import os.path

#goddesses

#imgur api https://api.imgur.com/oauth2
#praw api http://praw.readthedocs.io/en/stable/index.html#main-page
#gfycat api https://developers.gfycat.com/api/

global imgur_client_id 
imgur_client_id =
gfycat_client_id = 

def get_pics_by_subreddit(subreddit, limit):
	user_agent = "windows:testing_agent:0.1 (by /u/Domuska)"
	reddit = praw.Reddit(user_agent = user_agent)
	thing_limit = limit
	
	#get submissions
	submissions = reddit.get_subreddit(subreddit).get_hot(limit=thing_limit)
	
	path = 'C:/scraper/'
	#variable that is used in file names
	variable = 1
	
	for submission in submissions:
		print ("\n")
		print(submission.url)
		url = submission.url
		filename = str(submission.author) + "-" + time.strftime("%Y_%m_%d_%I_%M")
		fullpath = os.path.join(path, filename)
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
					#urllib.request.urlretrieve(album_img_url, fullpath +  "_" + str(album_variable) + ".jpg")
					path_with_extension = fullpath +  "_" + str(album_variable) + ".jpg"
					save_image_with_url_path(album_img_url, path_with_extension)
					album_variable += 1
					
				
			#convert imgur links to pure picture links			
			#if i.imgur is in url, it is a direct link to the pic
			else:
				#if "i.imgur" not in url:
				image_data = handle_imgur_picture(url)
				
				if image_data['animated'] is True:
					print ("animated image!")
					url = image_data['mp4']
					#urllib.request.urlretrieve(url, fullpath + filename + ".mp4")
					path_with_extension = fullpath + ".mp4"
					save_image_with_url_path(url, path_with_extension)
					
				else:
					url = url + ".jpg"
					#urllib.request.urlretrieve(url, fullpath + filename + ".jpg")
					path_with_extension = fullpath + ".jpg"
					save_image_with_url_path(url, path_with_extension)
				
		
		elif "reddituploads" in url or "tumblr" in url: 
			if ".gif" in url:
				path_with_extension = fullpath + ".gif"
				save_image_with_url_path(url, path_with_extension)
			else:
				path_with_extension = fullpath + ".jpg"
				save_image_with_url_path(url, path_with_extension)
				
		#todo: properly handle gfycat urls, read API and implement
		#gfycat uses only https
		#todo fix, if html5 video is in giant domain this wont work
		#dirty fix, not nice, do something more reasonable
		elif "gfycat" in url:
			if ".webm" in url:
				path_with_extension = fullpath + ".webm"
				print (gfycat_url)
				save_image_with_url_path(gfycat_url, path_with_extension)
			elif ".mp4" in url:
				path_with_extension = fullpath + ".mp4"
				print (gfycat_url)
				save_image_with_url_path(gfycat_url, path_with_extension)
			else:
				#this try-catch is just for handling the zippy/giant/fat monstrosity
				try:
					path_with_extension = fullpath + ".webm"
					#url = 'zippy.' + url + '.webm'
					#direct urls to webms in gfycat have zippy/giant/fat and .webm extension in the url in these locations
					gfycat_url = url[:8] + 'zippy.' + url[8:] + ".webm"
					print (gfycat_url)
					save_image_with_url_path(gfycat_url, path_with_extension)
				except urllib.error.URLError as err:
					try:
						if err.code == 403:
							gfycat_url = url[:8] + 'giant.' + url[8:] + ".webm"
							print (gfycat_url)
							save_image_with_url_path(gfycat_url, path_with_extension)
					except urllib.error.URLError as err2:
						if err2.code == 403:
							gfycat_url = url[:8] + 'fat.' + url[8:] + ".webm"
							print (gfycat_url)
							save_image_with_url_path(gfycat_url, path_with_extension)
				
		
		variable += 1
			
			
			
def save_image_with_url_path(url, path):
	urllib.request.urlretrieve(url, path)
	
#helper method to handle an imgur album
#as parameter takes the ID of the album
#returns: dictionary that has the info that album API returns			
def handle_imgur_album(album_url):

	try:
		#get the point where album url starts, using re and a regex
		regex = re.search('/a/', album_url)
		#splice the id from the whole url
		album_id = album_url[regex.end():]
		print("album_id: " + album_id)
		
		#use the album api to get urls to the individual images
		gallery_endpoint_url = "https://api.imgur.com/3/album/" + album_id + "/images"
		#add my own client-id to the request as header
		headers = {'Authorization' : 'Client-ID ' + imgur_client_id }
		request = urllib.request.Request(gallery_endpoint_url, None, headers)
		#get the response
		response = urllib.request.urlopen(request)
		
		#decode the response with utf-8 (hopefully correct)
		response_str = response.read()
		response_str = response_str.decode('utf-8')
		#print(response_str)
		
		data = json.loads(response_str)
		#return only the 'data' portion
		return data['data']
	except urllib.error.URLError as err:
		print ("Error code: " + err.code)
		print ("Reason: " + err.reason)
		print ("Headers: " + err.headers)
	
def handle_imgur_picture(picture_url):
	try:
		#get the pic id with regexes
		regex = re.search('.com/', picture_url)
		pic_id = picture_url[regex.end():]
		
		#handle common file extensions
		if 'gifv' in pic_id:
			#pic_id = pic_id[: - pic_id.find('.') + 2]
			pic_id = pic_id[:-5]
		elif '.jpg' in pic_id or '.gif' in pic_id or '.mp4' in pic_id:
			#pic_id = pic_id[: - pic_id.find('.') +1]
			pic_id = pic_id[:-4]
			
		print ("pic id: " + pic_id)
		#use the image api to get image metadata
		image_endpoint_url = "https://api.imgur.com/3/image/" + pic_id
		
		#add client ID as header
		headers = {'Authorization' : 'Client-ID ' + imgur_client_id}
		
		#build request
		request = urllib.request.Request(image_endpoint_url, None, headers)
		#get response
		response = urllib.request.urlopen(request)
		
		response_str = response.read()
		response_str = response_str.decode('utf-8')
		
		data = json.loads(response_str)
		return data['data']
		
	except urllib.error.URLError as err:
		print ("Error code: " + err.code)
		print ("Reason: " + err.reason)
		print ("Headers: " + err.headers)
	