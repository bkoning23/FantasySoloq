'''
Created on Jul 1, 2014

@author: Brendan
'''

import requests
import mysql.connector as mariadb
from Constants import *
import time

def getSummonerId(region, summonerName):
	summonerName = summonerName.lower()
	region = region.lower()
	
	#Database connection to check if the summoner ID is already in the database from a previous request
	databaseConnection = mariadb.connect(user=databaseUser, password=databasePassword, database=databaseName)
	cursor = databaseConnection.cursor()
	cursor.execute("SELECT summonerID FROM Summoners WHERE summonerName=%s", (summonerName,))
	row = cursor.fetchone()
	if(row is not None):
		id = row[0]
		cursor.close()
		databaseConnection.close()
		return id
	cursor.close()
	databaseConnection.close()
	#Database connection to add the summonerID to the database to reduce API calls in the future
	databaseConnection = mariadb.connect(user=databaseUser, password=databasePassword, database=databaseName)
	cursor1 = databaseConnection.cursor()
	print ("API CALL")
	url = 'https://'+ region + '.api.pvp.net/api/lol/' + region + '/v1.4/summoner/by-name/' + summonerName + '?api_key=ec23e4b8-9674-4c38-8904-861ef246aa2b'
	time.sleep(2)
	r = requests.get(url)
	if (r.status_code != 200):
		return ("Error") 
	else:
		r = r.json()
		id = r[summonerName]['id']
		cursor1.execute("INSERT INTO Summoners (summonerID, summonerName) VALUES (%s,%s)", (id, summonerName))
		print('Inserted into Summoners Table', summonerName)
		databaseConnection.commit()
		cursor1.close()
		databaseConnection.close()
		return id
    
def getSummonerGames(region, summonerId):
	url = 'https://' + region + '.api.pvp.net/api/lol/' + region + '/v1.3/game/by-summoner/' + str(summonerId) + '/recent?api_key=ec23e4b8-9674-4c38-8904-861ef246aa2b'
	print ("API CALL")
	time.sleep(2)
	r = requests.get(url)
	if (r.status_code != 200):
		return ("Error") 
	else:
		r = r.json()
		return r

 