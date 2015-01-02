'''
Created on Jul 1, 2014

@author: Brendan
'''
import riotAPI
from pprint import pprint

def getRecentGameOnlyStats(region, summonerName):
	summonerId = riotAPI.getSummonerId(region, summonerName)
	games = riotAPI.getSummonerGames(region, summonerId)
	if ((summonerId == "Error") or (games == "Error")):
		return "Error"
	else:
		return (games['games'][0]['stats'], games['games'][0]['subType'])

