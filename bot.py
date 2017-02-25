#!/usr/bin/python

#Regular Imports
import discord
import time
import requests
import random
import asyncio
from discord import opus

#Misc. Imports
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

#Globals
client = discord.Client()
LoLAPIKey = "c9b56d96-d3e4-4914-8a9f-11d2398f7e75"
token = "MTc3OTcyNTYzMjYyMTc3Mjkw.Cg2VXQ.ABZJFjBtFesUIKk9q3E5797M6AU"

#Youtube Playlist Controls
PLAYER_CTRL = ""
def playerStart():
	global PLAYER_CTRL
	PLAYER_CTRL = "START"
	return

def playerPause():
	global PLAYER_CTRL
	PLAYER_CTRL = "PAUSE"
	return

def playerSkip():
	global PLAYER_CTRL
	PLAYER_CTRL = "SKIP"
	return

#League Methods
def requestSummonerData(summonerName, LoLAPIKey):
	URL = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/" + summonerName + "?api_key=" + LoLAPIKey
	response = requests.get(URL)

	return response.json()

def requestRankedData(ID, LoLAPIKey):

	URL = "https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/" + ID + "/entry?api_key=" + LoLAPIKey
	response = requests.get(URL)

	return response.json()

def requestCurrentGame(ID, LoLAPIKey):

	URL = "https://na.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/NA1/" + ID + "?api_key=" + LoLAPIKey
	response = requests.get(URL)

	if "404" in str(response):
		return "No"
	else:
		return "Yes"

#Utility Methods
def opus():
	opus_libs = ['libopus-0.x86.dll','libopus-0.x64.dll','libopus-0.dll','libopus.so.0','libopus.0.dylib']
	if opus.is_loaded() is True:
		return
	else:
		for opus_lib in opus_libs:
			try:
				opus.load_opus(opus_lib)
			except OSError:
				pass

#Discord Methods
def greet(author, message):
	yield from client.send_message(message.channel,"Hello {0.author.mention}! I hope you are having a wonderful day.".format(message))

def choose(author, message):
	names = message.content[8:].split(" ")
	time.sleep(2)
	yield from client.send_message(message.channel, random.choice(names) + ", you have been chosen!".format(message))

@asyncio.coroutine
def youtube(author, message):
	URL = message.content[9:]
	print("The URL is:" + URL)
	voice = None
	player = None
	if URL and URL.startswith("https://www.youtube.com/"):
		voice = yield from client.join_voice_channel(author.voice_channel)
		player = yield from voice.create_ytdl_player(URL)
	else:
		yield from client.send_message(message.channel, "{0.author.mention}, That is not a valid URL.".format(message))
		return

	if voice is not None and voice.is_connected() and URL:
		player.start()

	#Player control loop
	while True:
		print("in the while")
		print(PLAYER_CTRL)
		if player is not None and PLAYER_CTRL is "SKIP":
			#TODO
			print("x")
		elif player is not None and PLAYER_CTRL is "START":
			player.resume()
		elif player is not None and PLAYER_CTRL is "PAUSE":
			player.pause()
		elif player is not None and "stopped" in str(player.is_playing) and PLAYER_CTRL is not "STOP": #The player has stopped playing due to the video ending
			yield from voice.disconnect()
			break
		yield from asyncio.sleep(1)

def league(author, message):
	summonerName = message.content[7:]
	responseJSON = requestSummonerData(summonerName, LoLAPIKey)

	if "Not Found" in str(responseJSON):
		print("in the if")
		yield from client.send_message(message.channel, "Sorry, {0.author.mention}. That summoner does not exist.".format(message))

	ID = responseJSON[summonerName.replace(" ","").lower()]['id']
	ID = str(ID)
	summonerLevel = str(responseJSON[summonerName.replace(" ","").lower()]['summonerLevel'])
	responseJSON2 = requestRankedData(ID, LoLAPIKey)
	inGame = requestCurrentGame(ID, LoLAPIKey)

	if summonerLevel == "30":
		yield from client.send_message(message.channel, "Hey {0.author.mention}, Here is the information you requested:\n"
		"\nName: ".format(message) + summonerName +
 		"\nLevel: " + summonerLevel +
		"\nRank: " + responseJSON2[ID][0]["tier"] + " " + str(responseJSON2[ID][0]["entries"][0]["division"]) + " @ " + str(responseJSON2[ID][0]["entries"][0]["leaguePoints"]) + "LP" +
		"\nIn Game: " + inGame +
		"\nMore Info: " + "http://na.op.gg/summoner/userName=" + summonerName.replace(" ","")
		)
	else:
		yield from client.send_message(message.channel, "Hey, {0.author.mention}, Here is the information you requested:\n"
		"\nName: ".format(message) + summonerName +
		"\nLevel: " + summonerLevel +
		"\nIn Game: " + inGame +
		"\nMore Info: " + "http://na.op.gg/summoner/userName=" + summonerName.replace(" ","")
		)

@asyncio.coroutine
def status(author, message): #TODO
	status = message.content[8:]
	print(status)
	client.change_status(1)

def test(author, message): #TODO
	member = discord.Member()
	print(member)
def help(author, message):
	yield from client.send_message(message.channel, "Commands:\n"
					"\n!greet"
					"\n!snipe [username]"
					"\n!choose [options, space seperated]"
					"\n!youtube [url]")

@client.event
@asyncio.coroutine
def on_message(message):
	author = message.author
	if   message.content.startswith("!greet"):
		yield from greet (author, message)
	elif message.content.startswith("!help"):
		yield from help  (author, message)
	elif message.content.startswith("!snipe"):
		yield from league(author, message)
	elif message.content.startswith("!choose"):
		yield from choose(author, message)
	elif message.content.startswith("!music"):
		yield from music(author, message)
	elif message.content.startswith("!youtube"):
		yield from youtube(author, message)
	elif message.content.startswith("!status"): #TODO
		yield from status(author, message)
	elif message.content.startswith("!test"): #TODO
		yield from test(author, message)
	elif message.content.startswith("!start") and PLAYER_CTRL is "PAUSE":
		playerStart()
	elif message.content.startswith("!pause") and PLAYER_CTRL is "" or PLAYER_CTRL is "START":
		playerPause()
	elif message.content.startswith("!skip") and PLAYER_CTRL is "START":
		playerSkip()

#Initiate Bot
#opus()
client.run("MTc3OTcyNTYzMjYyMTc3Mjkw.Cg2VXQ.ABZJFjBtFesUIKk9q3E5797M6AU")
