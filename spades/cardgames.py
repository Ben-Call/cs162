#!/usr/bin/env python3.3
# -*- coding: utf-8 -*-

# Credit goes to Lee Ehudin for the Card class and the Deck class, as he posted this on the wiki earlier when I was working on this
# I made a few minor changes, such as coloring the text, making the Ace high, and getting rid of the symbols for purposes of readability
# I also added the functions at the end, and the three classes at the end


"""A module defining functions for playing card games"""

import random
import itertools
from termcolor import colored

class Card(object):
    """Defines a Card class for easy access to a card's suit and value"""
# Put Ace at the end of values because Ace is high in Spades
    VALUES = ('2', '3', '4', '5', '6', '7', '8', '9', '10',
              'Jack', 'Queen', 'King', 'Ace')
    SUITS = ('Clubs', 'Diamonds', 'Hearts', 'Spades')
    ALIASES = {'J':'Jack', 'Q':'Queen','K':'King','A':'Ace'}
    SUIT_ALIAS = {'c':'Clubs', 'd':'Diamonds','h':'Hearts','s':'Spades'}

    def __init__(self, value, suit):
        self.value = str(value)
        self.suit = str(suit)

    def __eq__(self, other):
        if isinstance(other, Card) and \
        self.value == other.value and self.suit == other.suit:
            return True
        else:
            return False

    def __str__(self):
        val = self.value
        suit = self.suit

        if val == 'Clubs':
            return colored("{} of {}".format(suit, val), 'cyan')
        elif val == 'Diamonds':
            return colored("{} of {}".format(suit, val), 'red')
        elif val == 'Hearts':
            return colored("{} of {}".format(suit, val), 'magenta')
        else:
            return colored("{} of {}".format(suit, val), 'yellow')

    def __repr__(self):
        return str([self.value, self.suit])

    def __lt__(self, other):
        return ((self.value, self.VALUES.index(self.suit)) < (other.value, self.VALUES.index(other.suit)))

    def number(self):
        return self.suit

    def type(self):
        return self.value

class Deck(object):

    def __init__(self, shuffled=True):
        self.deck = [Card(*card) \
                     for card in itertools.product(Card.SUITS, Card.VALUES)]
        if shuffled:
            self.shuffle()

    def __repr__(self):
        return ', '.join(map(repr,self.deck))

    def __str__(self):
        return ', '.join(map(str,self.deck))

    def __len__(self):
        return len(self.deck)

    def __getitem__(self, val):
        return self.deck[val]

    def __iter__(self):
        return iter(self.deck)

    def shuffle(self):
        new_deck = []
        while self.deck:
            rand = random.randrange(len(self.deck))
            new_deck.append(self.deck.pop(rand))
        self.deck = new_deck

    def draw(self):
        return self.deck.pop(0)

# Creates a class of knowledge that the computer AI could have about the game state
class Knowledge(object):
    def __init__(self, cards_left, teammate, opponent1, opponent2):
        self.cards_left = cards_left
        self.teammate = teammate
        self.opponent1 = opponent1
        self.opponent2 = opponent2

class Player(object):
    def __init__(self, name, hand, tricks, contract, score, team, lastTrick, isAI, knowledge):
        self.name = str(name)
        self.hand = hand
        self.tricks = int(tricks)
        self.contract = int(contract)
        self.score = int(score)
        self.team = team
        self.lastTrick = lastTrick
        self.isAI = isAI
        self.knowledge = knowledge

        def __str__(self):
            return "{} bid {} and took {} tricks".format(self.name, self.contract, self.tricks)
        
        def __repr__(self):
            return str([self.name, self.hand, self.tricks, self.contract, self.team, self.lastTrick])


class Team(object):
    def __init__(self, name, player1, player2, score):
        self.name = name
        self.player1 = player1
        self.player2 = player2
        self.score = int(score)

    def __str__(self):
        return "{} have a score of {}".format(self.name, self.score)
    
    def __repr__(self):
        return str([self.name, self.player1, self.player2, self.score])

    def contract(self):
        return (self.player1.contract + self.player2.contract)
    
    def tricks(self):
        return (self.player1.tricks + self.player2.tricks)

# Returns the number of cards in a list of cards of a given suit
def numberInSuit(hand, suit):
    return len(list(filter(lambda x: suit==x.type(), hand)))

# Returns a list of valid next moves based off of a given hand
# The restriction should be a suit, or None
# Spades_broken is a boolean value
def validOptions(hand, restriction, spades_broken):
    if (restriction is None) and numberInSuit(hand, 'Spades') != len(hand) and not spades_broken:
        return list(filter(lambda x: x.type() != 'Spades', hand))
    elif numberInSuit(hand, restriction) == 0:
        return hand
    else:
        return list(filter(lambda x: restriction == x.type(), hand))

# This returns the highest card in a given suit out of a collection of cards
# It takes spades_broken as an argument so as to maintain compatibility with validOptions
def highestInSuit(cards, suit, spades_broken):
    if numberInSuit(cards, suit) == 0:
        return None
    else:
        valid_cards = validOptions(cards, suit, spades_broken)
        valid_cards.sort()
        return valid_cards[-1]
