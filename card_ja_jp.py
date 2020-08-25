from twisted_fate import Card
from pathlib import Path
import glob
import json
from utils import read_json_file

dataDir = Path(__file__).parent / "data"

try:
	cardsFiles = glob.glob("data/set*.json")
	allCards = []
	for jsonFile in cardsFiles:
		with open(jsonFile, mode='r', encoding='utf8') as f:
			f_json = json.load(f)
		allCards += f_json
except Exception as e:
	print("Could not load card ja_jp data")

class Card_ja_jp:
	def __init__(self, card):
		self.card = card
		self.name = [card for card in allCards if card["cardCode"] == self.card.cardCode][0]["name"]
		self.count = self.card.count

	def __repr__(self):
		return f"Card_ja_jp({self.card.cardCode}, Name: {self.name}, Count: {self.count})"
