from twisted_fate_jp import Deck

class TypedDeck:
	def __init__(self, deckCode:str, deck:Deck=None):
		self.deck = Deck.decode(deckCode)
		if deck is not None:
			self.deck = Deck
		self._reloadDeck()

	def _reloadDeck(self):
		self.cards = self._sortCards(self.deck.cards)
		self.units = list(filter(lambda card: card.cardType == "ユニット", self.cards))
		self.spells = list(filter(lambda card: card.cardType == "スペル", self.cards))
		self.landmarks = list(filter(lambda card: card.cardType == "ランドマーク", self.cards))
		self.champions = list(filter(lambda card: card.superType == "チャンピオン", self.units))
		self.followers = list(filter(lambda card: card.superType == "", self.units))
		self.regions = set([card.region for card in self.cards])

	def _sortCards(self, cards):
		return sorted(cards, key=lambda card: card.cost)
	
	def subtractDeck(self, deck: Deck):
		for c in deck.cards:
			self.deck.subtractCard(c)
		self._reloadDeck()