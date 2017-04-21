import praw, urllib, json, time, re, api_keys
import os.path

#for web requests
import requests

#for exception logging purposes in the get_pics_by_subreddit
import traceback
import logging

#imgur api https://api.imgur.com/oauth2
#praw api http://praw.readthedocs.io/en/stable/index.html#main-page
#gfycat api https://developers.gfycat.com/api/

def get_pics_by_subreddit(subreddit, limit):
		
	global imgur_client_id
	imgur_client_id = api_keys.imgur_client_id
	global gfycat_client_id
	gfycat_client_id = api_keys.gfycat_client_id
	global gfycat_client_secret
	gfycat_client_secret = api_keys.gfycat_client_secret
	
	
	user_agent = "windows:testing_agent:0.1 (by /u/Domuska)"
	reddit = praw.Reddit(user_agent = user_agent, client_id = 'xyvZRr2fAFmFfg', client_secret = None)
	thing_limit = limit
	
	#get submissions
	#submissions = reddit.get_subreddit(subreddit).get_hot(limit=thing_limit)
	submissions = reddit.subreddit(subreddit).hot(limit=thing_limit)
	
	path = 'C:/scraper/' + subreddit
	#variable that is used in file names
	variable = 1
	
	
	try:
		if not os.path.exists(path):
			os.makedirs(path)
			
			
		global images_downloaded
		images_downloaded = 0
		global albums_downloaded
		albums_downloaded = 0
		global videos_downloaded
		videos_downloaded = 0
		
		for submission in submissions:
			print ("\n")
			print(submission.url)
			url = submission.url
			#use submission name as file name
			title = submission.title
			
			#http://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python
			#remove reserved windows characters
			title = slugify(title)
			#if reddit submission title only contains unallowed characters, add something as title
			if len(title) == 0:
				title = variable
			filename = title + "_" + str(submission.author) + "_" + str(variable)
			
			fullpath = os.path.join(path, filename)
			
			#handle imgur separate from other image sources, imgur can have 
			#albums and animated videos
			if "imgur" in url:
				try:
					download_from_imgur(url, filename, path)
				except urllib.error.URLError as err:
					print ("Error code: " + str(err.code))
					print ("Reason: " + err.reason)
					print ("Headers: " + err.headers)
					
					if err.code == 429:
						print ("Stopping downloads, daily limit reached")
						return 0
					
			
			elif "reddituploads" in url or "tumblr" in url: 
				if ".gif" in url:
					path_with_extension = fullpath + ".gif"
					save_image_with_url_path(url, path_with_extension)
					images_downloaded += 1
				else:
					path_with_extension = fullpath + ".jpg"
					save_image_with_url_path(url, path_with_extension)
					images_downloaded += 1
					
					
					
			#https://gfycat.com/PessimisticReadyFrog
			#todo: properly handle gfycat urls, read API and implement
			#gfycat uses only https
			#dirty fix, not nice, do something more reasonable, use API maybe to ask in which domain the video is?
			elif "gfycat" in url:
				#use a wizard's spell to reverse the url string
				gfy_id = url[::-1]
				print(gfy_id)
				regex = re.search('/', gfy_id)
				gfy_id = gfy_id[:regex.end()-1]
				gfy_id = gfy_id[::-1]
				print(gfy_id)
				download_from_gfycat_with_id(gfy_id, filename, path)
				
				
				
				#if "https" not in url:
				#	url = url[:4] + 's' + url[4:]
				#if ".webm" in url:
				#	path_with_extension = fullpath + ".webm"
				#	print (gfycat_url)
				#	save_image_with_url_path(gfycat_url, path_with_extension)
				#elif ".mp4" in url:
				#	path_with_extension = fullpath + ".mp4"
				#	print (gfycat_url)
				#	save_image_with_url_path(gfycat_url, path_with_extension)
				#else:
				#	#this try-catch is just for handling the zippy/giant/fat monstrosity
				#	try:
				#		path_with_extension = fullpath + ".webm"
				#		#url = 'zippy.' + url + '.webm'
				#		#direct urls to webms in gfycat have zippy/giant/fat and .webm extension in the url in these locations
				#		gfycat_url = url[:8] + 'zippy.' + url[8:] + ".webm"
				#		print (gfycat_url)
				#		save_image_with_url_path(gfycat_url, path_with_extension)
				#	except urllib.error.URLError as err:
				#		try:
				#			if err.code == 403:
				#				gfycat_url = url[:8] + 'giant.' + url[8:] + ".webm"
				#				print (gfycat_url)
				#				save_image_with_url_path(gfycat_url, path_with_extension)
				#		except urllib.error.URLError as err2:
				#			try:
				#				if err2.code == 403:
				#					gfycat_url = url[:8] + 'fat.' + url[8:] + ".webm"
				#					print (gfycat_url)
				#					save_image_with_url_path(gfycat_url, path_with_extension)					
				#			except urllib.error.URLError as err3:
				#				if err3.code == 403:
				#					print("Error 403, could not save video at url: " + gfycat_url)
							
			
			variable += 1
				
		print("\n\nDownload finished!\n")
		print("Images downloaded: " + str(images_downloaded) + "\n")
		print("Videos downloaded: " + str(videos_downloaded) + "\n")
		print("Albums downloaded: " + str(albums_downloaded))
	
	except Exception as e:
		logging.error(traceback.format_exc())
			
def save_image_with_url_path(url, path):
	print(urllib.request.urlretrieve(url, path))
	
#download an webm from gfycat with the gfycat ID supplied
def download_from_gfycat_with_id(gfy_id, filename, gfy_path = 'C:\scraper\gfycat_webms\\'):

	global images_downloaded
	global albums_downloaded
	global videos_downloaded
	
	try:
		client_id = gfycat_client_id
		token_request_url = 'https://api.gfycat.com/v1/oauth/token'
		
		#requests kirjaston kikkailut
		results = requests.get(token_request_url, params = {
													'grant_type':'client_credentials',
													'client_id':client_id,
													'client_secret':gfycat_client_secret})
		#print("response from gfycat: " + results.text)
		#result_dictionary = json.loads(results.json())
		token = results.json()['access_token']
		#token = results_dictionary['access_token']
		print (token)
		
		#get info about the GFY requested
		gfy_request_url = 'https://api.gfycat.com/v1/gfycats/'
		gfy_request_url += gfy_id
		results = requests.get(gfy_request_url, headers={
													"Authorization": token})
										
		#get the URL and name of the GFY
		#print("gfy request response: " + results.text)
		webm_url = results.json()['gfyItem']['webmUrl']
		webm_name = results.json()['gfyItem']['gfyName'] + ".webm"
		print ('webm url : ' + webm_url)
		
		gfy_path = os.path.realpath(gfy_path)
		if not os.path.exists(gfy_path):
			os.makedirs(gfy_path)
		
		gfy_path = os.path.join(gfy_path, filename)
		gfy_path = gfy_path + "_" + webm_name
		#filepath = os.path.join(gfy_path, webm_name)
		
		#save the GFY from the URL
		print(urllib.request.urlretrieve(webm_url, gfy_path))
		videos_downloaded += 1
		
	except urllib.error.URLError as err:
		print ("Error code: " + str(err.code))
		print ("Reason: " + err.reason)
		print ("Headers: " + err.headers)
	

#download an arbitrary image or album from imgur
#	url : the URL of the imgur image or album
#	path : the path to the image along with the file name (example, 'c:\pics\catpicture')
#the file will be saved to the path provided, if the URL goes to an album _IMAGENUMBER will be
#added after the file name
def download_from_imgur(url, filename, image_path = 'C:\scraper\imgur\\', ):

	global images_downloaded
	global albums_downloaded
	global videos_downloaded
	
	#make sure the folder path exists
	if not os.path.exists(image_path):
		os.makedirs(image_path)
	
	#join the file path and file name
	full_file_path = os.path.join(image_path, filename)
	
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
			#add the album variable and file extension to file path
			path_with_extension = full_file_path +  "_" + str(album_variable) + ".jpg"
			save_image_with_url_path(album_img_url, path_with_extension)
			album_variable += 1
			images_downloaded += 1
			albums_downloaded += 1
			
					
				
	#convert imgur links to pure picture links			
	#if i.imgur is in url, it is a direct link to the pic
	else:
		#if "i.imgur" not in url:
		image_data = handle_imgur_picture(url)
		
		if image_data['animated'] is True:
			print ("animated image!")
			url = image_data['mp4']
			#urllib.request.urlretrieve(url, fullpath + filename + ".mp4")
			#add the correct file extension to file path
			path_with_extension = full_file_path + ".mp4"
			save_image_with_url_path(url, path_with_extension)
			videos_downloaded += 1
			
		else:
			url = url + ".jpg"
			#urllib.request.urlretrieve(url, fullpath + filename + ".jpg")
			#add the extension to file path
			path_with_extension = full_file_path + ".jpg"
			save_image_with_url_path(url, path_with_extension)
			images_downloaded += 1
					

#helper method to handle an imgur album
#as parameter takes the ID of the album
#returns: dictionary that has the info that album API returns			
def handle_imgur_album(album_url):

	try:
		#get the point where album url starts, using re and a regex
		if "/a/" in album_url:
			regex = re.search('/a/', album_url)
		else:
			regex = re.search('/gallery/', album_url)
		#splice the id from the whole url
		album_id = album_url[regex.end():]
		
		#the ID can have some extra stuff after url, like: ?branch_used=true
		regex = re.search('\?', album_id)
		if regex is not None:
			album_id = album_id[:regex.start()]
		
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
		print ("Error code: " + str(err.code))
		print ("Reason: " + err.reason)
		print ("Headers: " + err.headers)
	
	
#returns: dictionary containing that has the info that the API provides of the picture
def handle_imgur_picture(picture_url):
	try:
		#get the pic id with regexes
		regex = re.search('.com/', picture_url)
		pic_id = picture_url[regex.end():]
		
		#handle common file extensions
		#if 'gifv' in pic_id:
			#pic_id = pic_id[: - pic_id.find('.') + 2]
			#pic_id = pic_id[:-5]
			#dot_position = pic_id.find('.')
			#pic_id = pic_id[:dot_position]
		#elif '.jpg' in pic_id or '.gif' in pic_id or '.mp4' in pic_id:
			#pic_id = pic_id[: - pic_id.find('.') +1]
		#	pic_id = pic_id[:-4]
		dot_position = pic_id.find('.')
		if dot_position != -1:
			pic_id = pic_id[:dot_position]
		
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
		print ("Error code: " + str(err.code))
		print ("Reason: " + str(err.reason))
		print ("Headers: " + str(err.headers))
		
#http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
#modified for python 3 from above answer
def slugify(value):
	"""
	Normalizes string, converts to lowercase, removes non-alpha characters,
	and converts spaces to hyphens.
	"""
	import unicodedata
	value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
	value = value.decode('utf-8')
	value = re.sub('[^\w\s-]', '', value)
	value = re.sub('[-\s]+', '-', value)
	return value
	