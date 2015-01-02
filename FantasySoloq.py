'''
Created on Jul 1, 2014

@author: Brendan
'''

import praw
import time
from pprint import pprint
import re
from collections import deque
import threading
from getGames import getRecentGameOnlyStats
import mysql.connector as mariadb
from Constants import *

#Connects and logs in to reddit
user_agent = ("FantasySoloQ 1.0 by /u/Cookieking")
r = praw.Reddit(user_agent=user_agent)
r.login(username='FantasySoloQ_Bot', password='sarahh12')

#Array for posts that have been scanned already.
already_done = []
#Current users and regions to be processed.
d1 = deque()
d2 = deque()
subreddit = r.get_subreddit('fantasysoloq')
regions = ['na', 'br', 'eune', 'euw', 'kr', 'lan', 'las', 'aus', 'ru', 'tr']

assistValue = 0.5
killValue = 2
deathValue = -1
csValue = 0.01


#This method pulls data from the reddit post to be added to the deque.
#Connects to reddit API with PRAW

def processPosts():
	while True:
		for submission in subreddit.get_new(limit=15):
			submission.save(unsave=False)
			title = submission.title.lower().replace(" ", "")
			info = re.match(r'\[(.*?)\]\[(.*?)\]', title)
			try:
				region = info.group(1)
				summonerName = info.group(2)
			except AttributeError:
				continue
			databaseConnection = mariadb.connect(user=databaseUser, password=databasePassword, database=databaseName)
			cursor = databaseConnection.cursor()
			cursor.execute("SELECT postID FROM Posts WHERE postID=%s", (submission.id,))
			row = cursor.fetchone()
			if(row is None):
				if(submission.id not in already_done):
					d1.append((summonerName, region, submission.id))
					already_done.append(submission.id);
			cursor.close()
			databaseConnection.close()
		#Number of seconds
		time.sleep(20)

#Takes each tuple in the deque and gets the necessary data to make the response.
#Connects to Riot API.
def getSummonerData():
	time.sleep(15)
	while True:
		while(len(d1) != 0):
			currentTuple = d1.popleft()
			tempName = currentTuple[0]
			tempRegion = currentTuple[1]
			tempPost = currentTuple[2]
			submission = r.get_submission(submission_id=tempPost)
			if (tempRegion not in regions):
				submission.add_comment("Invalid region")
				print("Invalid Region Removed")
				submission.remove(spam=False)
				continue
			tempData = getRecentGameOnlyStats(tempRegion, tempName)
			if (tempData[0] == "Error"):
				submission.add_comment("Invalid SummonerName.")
				print("Invalid SummonerName", tempName)
				submission.remove(spam=False)
				continue
			else:
				d2.append((currentTuple, tempData))
		print("Empty d1 queue, 30 second sleep")
		time.sleep(30)
		
def redditPost():
	time.sleep(25)
	while True:
		while(len(d2) != 0):
			tempData = d2.popleft()
			identification = tempData[0]
			data = tempData[1][0]
			queueType = tempData[1][1]
			submission = r.get_submission(submission_id=identification[2])
			
			try:
				championsKilled = data['championsKilled']
			except KeyError:
				championsKilled = 0
			try:
				minionsKilled = data['minionsKilled']
			except KeyError:
				minionsKilled = 0
			try:
				assists = data['assists']
			except KeyError:
				assists = 0
			try:
				deaths = data['numDeaths']
			except KeyError:
				deaths = 0
			
			killsPoints = championsKilled*killValue
			assistPoints = assists*assistValue
			minionPoints = (float(minionsKilled)*float(csValue))
			deathPoints = deaths*deathValue
			
			
			total = killsPoints + assistPoints + minionPoints + deathPoints
			
			comment = ("""Player: %s Region: %s\n Queue Type: %s\n
						
						Category | Count | Points
						:--|:--|:--
						Kills | %d | %d
						Assists | %d | %.2f
						CS | %d | %.2f
						Deaths | %d | %d
						Total Points | | %.2f""") % (identification[0], identification[1].upper(), queueType, championsKilled, killsPoints, assists, assistPoints, minionsKilled, round(minionPoints,2), deaths, deathPoints, round(total,2))
			submission.add_comment(comment)
			databaseConnection = mariadb.connect(user=databaseUser, password=databasePassword, database=databaseName)
			cursor = databaseConnection.cursor()
			cursor.execute("INSERT INTO Posts (postID) VALUES (%s)", (identification[2],))
			databaseConnection.commit()
			cursor.close()
			databaseConnection.close()
			print ('Inserted into Posts Table', identification[2])
			already_done.remove(identification[2])
			#print(identification)
			#print(data)
		print("Empty d2 queue, 30 second sleep")
		time.sleep(30)


t1 = threading.Thread(target = processPosts)
t2 = threading.Thread(target = getSummonerData)
t3 = threading.Thread(target = redditPost)

t1.daemon = True
t1.start()
t2.daemon = True
t2.start()     
t3.daemon = True
t3.start()   

print("Server Threads Running")  
      
while True:
	time.sleep(100000)
        
        
    
    
