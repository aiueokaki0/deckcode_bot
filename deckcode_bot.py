import discord
import re
import binascii
import os

from twisted_fate_jp import Deck
from typedDeck import TypedDeck

# const
botToken = os.getenv("DISCORD_BOT_TOKEN")
callCommand = r"/deck "
deckcode = r"[A-Z0-9]+"
emojis = {
	"champion": "<:champion:747822030384136343>",
	"follower": "<:follower:747822044216950784>",
	"spell": "<:spell:747822058225795104>",
	"landmark": "<:landmark:765914225842454539>",
	"all": "<:all:748188732548579338>",
	"bilgewater": "<:bilgewater:748188752806936646>",
	"demacia": "<:demacia:748188764001665177>",
	"freljord": "<:freljord:748188775137673257>",
	"ionia": "<:ionia:748188787451887736>",
	"noxus": "<:noxus:748188803201761410>",
	"piltoverzaun": "<:piltoverzaun:748188812802523170>",
	"shadowisles": "<:shadowisles:748188823426564147>",
	"targon": "<:targon:765899819096604673>"
	}

# function
def buildMessage(typedCards):
	result = ""
	for card in typedCards:
		regionEmoji = [v for k, v in emojis.items() if k == card.region][0]
		line = regionEmoji + "**" + str(card.cost) + "** " + card.name + " (**x"+ str(card.count) + "**)\n"
		result += line
	result += "------------\n"
	return result

def getTempDeckName(typedDeck):
	return "".join([card.name for card in typedDeck.champions])

# 接続に必要なオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
	print('[Info] start deckcode bot')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
	# メッセージ送信者がBotだった場合は無視する
	if message.author.bot:
		return
	# bot呼び出しコマンドだった場合デッキ情報を返す
	if re.match(callCommand, message.content):
		command = message.content.split()
		deckCode = command[1]
		
		try:
			deck = TypedDeck(deckCode)
			regionsEmoji = [v for k, v in emojis.items() for region in deck.regions if k == region]
			deckName = getTempDeckName(deck)
			if len(command) >= 3:
				deckName = command[2]

			embed = discord.Embed(title=deckName, description=" ".join(regionsEmoji), color=discord.Colour.green())
			championMessage = buildMessage(deck.champions)
			if len(deck.landmarks) > 0:
				landmarkMessage = emojis["landmark"] + "**ランドマーク**\n" + buildMessage(deck.landmarks)
				championMessage += landmarkMessage
			
			embed.add_field(name=emojis["champion"] + "チャンピオン",value=championMessage)
			embed.add_field(name=emojis["follower"] + "フォロワー",value=buildMessage(deck.followers))
			embed.add_field(name=emojis["spell"] + "スペル", value=buildMessage(deck.spells))
			
			await message.channel.send(embed=embed)
			print("[Info] " + deckCode + " " + deckName)

		except binascii.Error as e:
			print("[Error] " + str(e))
			embed = discord.Embed(title="Error", description="Wrong deckcode", color=discord.Colour.red())
			await message.channel.send(embed=embed)
		except Exception as e:
			print("[Error] " + str(e))
			embed = discord.Embed(title="Error", description="Something wrong", color=discord.Colour.red())
			await message.channel.send(embed=embed)

# Botの起動とDiscordサーバーへの接続
client.run(botToken)
