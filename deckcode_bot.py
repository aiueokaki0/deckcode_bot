import discord
import re
import binascii
import os

from twisted_fate_jp import Deck
from typedDeck import TypedDeck
from dotenv import load_dotenv

# const
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
botToken = os.getenv("BOT_TOKEN")
# 文末のスペースはdicord側で削除されて送信されるため引数なしのコマンドには反応しない
callCommands = {
	"decode": r";deck\s",
	"diff": r";diff\s",
	"help": r";help"
}
deckcode = r"[A-Z0-9]+"
emojis = {
	"champion": "<:champion:747822030384136343>",
	"follower": "<:follower:747822044216950784>",
	"spell": "<:spell:747822058225795104>",
	"landmark": "<:landmark:782176960808878100>",
	"equipment": "<:equipment:1014931401835028570>",
	"runeterra": "<:runeterra:748188732548579338>",
	"bilgewater": "<:bilgewater:748188752806936646>",
	"demacia": "<:demacia:748188764001665177>",
	"freljord": "<:freljord:748188775137673257>",
	"ionia": "<:ionia:748188787451887736>",
	"noxus": "<:noxus:748188803201761410>",
	"piltoverzaun": "<:piltoverzaun:748188812802523170>",
	"shadowisles": "<:shadowisles:748188823426564147>",
	"targon": "<:targon:765899819096604673>",
	"shurima": "<:shurima:816818401875722270>",
	"bandlecity": "<:bandlecity:880260012612661289>",
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

def buildDiffMessage(typedCards):
	result = ""
	for card in typedCards:
		regionEmoji = [v for k, v in emojis.items() if k == card.region][0]
		countStr = ""
		if card.count > 0:
			countStr = "+" + str(card.count)
		else:
			countStr = str(card.count)
		line = regionEmoji + "**" + str(card.cost) + "** " + card.name + " (**"+ countStr + "**)\n"
		result += line
	result += "------------\n"
	return result

def buildCountsMessage(typedDeck):
	result = (emojis["champion"] + "x" + str(typedDeck.counts[0]) + " "
				+ emojis["follower"] + "x" + str(typedDeck.counts[1]) + " "
				+ emojis["spell"] + "x" + str(typedDeck.counts[2]) + " "
				+ emojis["landmark"] + "x" + str(typedDeck.counts[3]) + " "
				+ emojis["equipment"] + "x" + str(typedDeck.counts[4]))
	return result

def getTempDeckName(typedDeck):
	return "".join([card.name for card in typedDeck.champions])

def diffDeck(deck1: TypedDeck, deck2: TypedDeck) -> TypedDeck:
	return deck2.subtractDeck(deck1)


# 接続に必要なオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
	# print(Deck(cards={"03PZ003":2, "03MT009": 2, "03NX007": 2}).to_deck_code())
	print('[Info][System] start deckcode bot')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
	# メッセージ送信者がBotだった場合は無視する
	if message.author.bot:
		return
	# 呼び出しコマンドか確認
	command = [v for k, v in callCommands.items() if re.match(v, message.content)]
	if command == []:
		return

	# bot呼び出しコマンドだった場合
	command = command[0]
	if command is not None:
		commandLine = message.content.split()
		# デッキ情報を返す
		if command == callCommands["decode"]:
			deckCode = commandLine[1]
			
			try:
				deck = TypedDeck(deckCode)
				regionsEmoji = [v for k, v in emojis.items() for region in deck.regions if k == region]
				deckName = getTempDeckName(deck)
				if len(commandLine) >= 3:
					deckName = commandLine[2]

				deckDescription = " ".join(regionsEmoji) + " | " + buildCountsMessage(deck)
				embed = discord.Embed(title=deckName, description=deckDescription, color=discord.Colour.green())
				championMessage = buildMessage(deck.champions)
				if len(deck.landmarks) > 0:
					landmarkMessage = emojis["landmark"] + "**ランドマーク**\n" + buildMessage(deck.landmarks)
					championMessage += landmarkMessage
				if len(deck.equipments) > 0:
					equipmentMessage = emojis["equipment"] + "**武具**\n" + buildMessage(deck.equipments)
					championMessage += equipmentMessage
				
				embed.add_field(name=emojis["champion"] + "チャンピオン",value=championMessage)
				embed.add_field(name=emojis["follower"] + "フォロワー",value=buildMessage(deck.followers))
				embed.add_field(name=emojis["spell"] + "スペル", value=buildMessage(deck.spells))
				
				await message.channel.send(embed=embed)
				print("[Info][decode] " + deckCode + " " + deckName)

			except binascii.Error as e:
				print("[Error][decode] " + str(e))
				embed = discord.Embed(title="Error", description="Wrong deckcode", color=discord.Colour.red())
				await message.channel.send(embed=embed)
			except Exception as e:
				print("[Error][decode] " + str(e))
				embed = discord.Embed(title="Error", description=str(e), color=discord.Colour.red())
				await message.channel.send(embed=embed)

		# 差分情報を返す
		elif command == callCommands["diff"]:
			if len(commandLine) < 3:
				print("[Error][diff] Wrong args")
				embed = discord.Embed(title="Error", description="usage: " + callCommands["diff"] + "[deckcode A] [deckcode B] ([name])", color=discord.Colour.red())
				await message.channel.send(embed=embed)
				return
			deckCodes = commandLine[1:3]
			try:
				decks = [TypedDeck(code) for code in deckCodes]
				countsMessages = [buildCountsMessage(d) for d in decks]
				# 両デッキのチャンピオン名の重複をなくしてコストでソート
				deckName = "diff: " + "".join([c[0] for c in sorted(list(set([(c.name, c.cost) for c in decks[0].champions + decks[1].champions])), key=lambda card:card[1])])
				if len(commandLine) >= 4:
					deckName = commandLine[3]
				
				# diff
				decks[1].subtractDeck(decks[0])
				diffDeck = decks[1]

				regionsEmoji = [v for k, v in emojis.items() for region in diffDeck.regions if k == region]
				deckDescription = " ".join(regionsEmoji) + " | " + countsMessages[0] + " -> " + countsMessages[1]
				embed = discord.Embed(title=deckName, description=deckDescription, color=discord.Colour.blue())
				championMessage = buildDiffMessage(diffDeck.champions)
				if len(diffDeck.landmarks) > 0:
					landmarkMessage = emojis["landmark"] + "**ランドマーク**\n" + buildDiffMessage(diffDeck.landmarks)
					championMessage += landmarkMessage
				if len(diffDeck.equipments) > 0:
					equipmentMessage = emojis["equipment"] + "**武具**\n" + buildDiffMessage(diffDeck.equipments)
					championMessage += equipmentMessage

				embed.add_field(name=emojis["champion"] + "チャンピオン",value=championMessage)
				embed.add_field(name=emojis["follower"] + "フォロワー",value=buildDiffMessage(diffDeck.followers))
				embed.add_field(name=emojis["spell"] + "スペル", value=buildDiffMessage(diffDeck.spells))
				
				await message.channel.send(embed=embed)
				print("[Info][diff] " + " ".join(deckCodes) + " " + deckName)

			except binascii.Error as e:
				print("[Error][diff] " + str(e))
				embed = discord.Embed(title="Error", description="Wrong deckcode", color=discord.Colour.red())
				await message.channel.send(embed=embed)
			except Exception as e:
				print("[Error][diff] " + str(e))
				embed = discord.Embed(title="Error", description=str(e), color=discord.Colour.red())
				await message.channel.send(embed=embed)


# Botの起動とDiscordサーバーへの接続
client.run(botToken)
