from twisted_fate import Deck
from card_ja_jp import Card_ja_jp

class TypedDeck:
	def __init__(self, deckCode):
		self.deck = Deck.decode(deckCode)
		self.cards = self._sortCards(self.deck.cards)

		self.cards_ja = [self._convCard_ja(card) for card in self.cards]

		self.units = list(filter(lambda c_ja: c_ja.card.cardType == "Unit", self.cards_ja))
		self.spells = list(filter(lambda c_ja: c_ja.card.cardType == "Spell", self.cards_ja))
		self.champions = list(filter(lambda c_ja: c_ja.card.superType == "Champion", self.units))
		self.followers = list(filter(lambda c_ja: c_ja.card.superType == "", self.units))

	def _sortCards(self, cards):
		return sorted(cards, key=lambda card: card.cost)

	def _convCard_ja(self, card):
		return Card_ja_jp(card)

