import discord
import re
import binascii
import os

from twisted_fate import Deck
from typedDeck import TypedDeck
from card_ja_jp import Card_ja_jp

# const
botToken = os.getenv("DISCORD_BOT_TOKEN")
callCommand = r"/deck "
deckcode = r"[A-Z0-9]+"
# imgDir = "img/cards_x25/"
# imgSuffix = ".png"
emojis = {"champion": "<:champion:747822030384136343>","follower": "<:follower:747822044216950784>", "spell": "<:spell:747822058225795104>"}

# function
def buildMessage(typedCards):
	result = ""
	for card_ja in typedCards:
		line = "**" + str(card_ja.count) + "** " + card_ja.name + "\n"
		result += line
	result += "------------\n"
	return result

def getTempDeckName(typedDeck):
	champions = typedDeck.champions
	result = ""
	for card_ja in champions:
		result += card_ja.name
	return result


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
			deckName = getTempDeckName(deck)
			if len(command) >= 3:
				deckName = command[2]

			embed = discord.Embed(title=deckName, color=discord.Colour.green())
			embed.add_field(name=emojis["champion"] + "チャンピオン",value=buildMessage(deck.champions))
			embed.add_field(name=emojis["follower"] + "フォロワー",value=buildMessage(deck.followers))
			embed.add_field(name=emojis["spell"] + "スペル", value=buildMessage(deck.spells))
			
			await message.channel.send(embed=embed)
			print("[Info] " + deckCode)

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


async def createDeckImg(cards):
	for card in deck.cards:
		imgPath = imgDir + card.cardCode + imgSuffix
		if not os.path.isfile(imgPath):
			await message.channel.send(content=card.name + " is not found")
		else:
			imgFile = discord.File(imgPath)
			await message.channel.send(file=imgFile)