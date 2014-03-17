#!/usr/bin/env python3.3
# Provides logic for the game's AI
# -*- coding: utf-8 -*-

import cardgames as c
import spades_engine as s
import pickle
import math

try:
    player_info = pickle.load(open("players.p", "rb"))
except FileNotFoundError:
    player_info = {}
    pickle.dump(player_info, open("players.p", "wb"))
#tree = ET.parse('players.xml')
#root = tree.getroot()
spades_broke = False

def middle(myList):
    if myList == []:
        return None
    else:
        return myList[math.ceil(len(myList)/2) - 1]

def winners(deck):
    winners = []
    for suit in c.Card.SUITS:
        options = cardsLeftInSuit(cardsLeft, suit)
        if options != []:
            winners.append(options[-1])
    return winners

def move(player, cards_played, spades_broken):
    global spades_broke
    spades_broke = spades_broken
    card = decide_move(player, cards_played)
#    if card in c.validOptions(player.hand, cards_played[0].type(), spades_broke):
#        pass
#    else:
#        print(cards_played)
#        print(card)
#        raise NameError('InvalidCard')
    cards_played.append(card)
    return cards_played

def cardsLeftInSuit(cards, suit):
    return list(filter(lambda x: x.type() == suit, cards))

def decide_move(player, cards_played):
    global cardsLeft

    cardsLeft = player.knowledge.cards_left

    index = len(cards_played)
    
    if player.knowledge.teammate[0] == 0 and player.knowledge.teammate[6] == 0:
        if index == 0:
            return nil_protect(player, cards_played)

        elif index == 1:

            if cards_played[0] in winners(cardsLeft) or player.knowledge.teammate[2 + c.Card.SUITS.index(cards_played[0].type())] == True:
                return protect(player, cards_played)

            elif c.numberInSuit(player.hand, cards_played[0].type()) == 0:
                return take(player, cards_played)

            elif list(filter(lambda x: c.Card.VALUES.index(x.number()) > c.Card.VALUES.index(cards_played[0].number()), c.validOptions(player.hand, cards_played[0].type(), spades_broke))) == []:
                return protect(player, cards_played)

            else:
                return c.highestInSuit(player.hand, cards_played[0].type(), spades_broke)
        else:
            if s.trick_winner(cards_played) != cards_played[0]:
                return protect(player, cards_played)
            else:
                return take(player, cards_played)
                        

    elif player.knowledge.opponent2[0] == 0 and player.knowledge.opponent2[6] == 0:
        if index == 3:
            if s.trick_winner(cards_played+[dump(player, cards_played)]) == cards_played[0]:
                return dump(player, cards_played)
            else:
                return c.validOptions(player.hand, cards_played[0].type(), spades_broke)[-1]
        else:
            return dump(player, cards_played)

    elif player.knowledge.opponent1[0] == 0 and player.knowledge.opponent1[6] == 0:
        if index != 0:
            if s.trick_winner(cards_played+[dump(player, cards_played)]) == cards_played[index - 1]:
                return dump(player, cards_played)
            else:
                return c.validOptions(player.hand, cards_played[0].type(), spades_broke)[-1]
        else:
            return dump(player, cards_played)
    else:
        return normal_move(player, cards_played)

def normal_move(player, cards_played):
    if player.contract == 0 and player.tricks == 0:
        card= dump(player, cards_played)
    elif player.contract + player.knowledge.teammate[0] + player.knowledge.opponent1[0] + player.knowledge.opponent2[0] > 11 or player.contract > player.tricks:
        if len(cards_played) == 3 and s.trick_winner(cards_played) == cards_played[1] and player.knowledge.teammate[0] < player.knowledge.teammate[6]:
            card = protect(player, cards_played)
        elif len(cards_played) == 2 and s.trick_winner(cards_played) == cards_played[0] in winners(cardsLeft) and c.numberInSuit(cardsLeft, cards_played[0].type()) - c.numberInSuit(player.hand, cards_played[0].type()) >= 3:
            card = protect(player, cards_played)
        else:
            card = take(player, cards_played)            
    else:
       card = dump(player, cards_played)
    return card


def nil_protect(player, cards_played):
    teammate = player.knowledge.teammate
    if c.numberInSuit(c.validOptions(player.hand, None, spades_broke), 'Spades') != 0:
        return cardsLeftInSuit(c.validOptions(player.hand, None, spades_broke), 'Spades')[-1]
    
    for suit in [x.type() for x in c.validOptions(player.hand, None, spades_broke)]:
        if (teammate[c.Card.SUITS.index(suit) + 1] == True) or cardsLeftInSuit(player.hand, suit) == cardsLeftInSuit(cardsLeft, suit):
            return c.highestInSuit(player.hand, suit, spades_broke)
    
    if list(filter(lambda x: x in winners(cardsLeft), c.validOptions(player.hand, None, spades_broke))) != []:
        return list(filter(lambda x: x in winners(cardsLeft), player.hand))[0]
    
    last_resort = c.validOptions(player.hand, None, spades_broke)[-1]
    for card in c.validOptions(player.hand, None, spades_broke):
        if card.number() > last_resort.number():
            last_resort = card
    return last_resort


def dump(player, cards_played):
    usable_cards = [card for card in list(filter(lambda x: x not in winners(cardsLeft), player.hand))]
    usable_suits = [x.type() for x in usable_cards]
    if usable_cards == []:
        usable_cards = player.hand
    usable_suits = [x.type() for x in usable_cards]
    if 'Spades' in usable_suits and usable_suits != ['Spades']:
        usable_suits.remove('Spades')

    if len(cards_played) == 0 and len(player.hand) != c.numberInSuit(player.hand, 'Spades'):
        base = 1
        for suit in usable_suits: # Find the longest non-trump suit
            if (player.knowledge.teammate[c.Card.SUITS.index(suit) + 1] == True) and 0 < c.numberInSuit(usable_cards, suit) < c.numberInSuit(cardsLeft, suit):
                card = cardsLeftInSuit(usable_cards, suit)[0]
                break
            elif c.numberInSuit(cardsLeft, suit) - c.numberInSuit(usable_cards, suit) >= base:
                base = c.numberInSuit(cardsLeft, suit)
                card = cardsLeftInSuit(usable_cards, suit)[0]
            else:
                card = usable_cards[0]

    elif len(cards_played) == 0:
        card = cardsLeftInSuit(usable_cards, 'Spades')[0]

    elif c.numberInSuit(player.hand, cards_played[0].type()) != 0:
        usable_cards = [card for card in list(filter(lambda x: x != s.trick_winner(cards_played+[x]), c.validOptions(player.hand, cards_played[0].type(), spades_broke)))]

        if usable_cards == []:
            usable_cards = c.validOptions(player.hand, cards_played[0].type(),spades_broke)
            if len(cards_played) != 3:
                usable_cards.reverse()
        card = usable_cards[-1]

    elif c.numberInSuit(player.hand, 'Spades') != len(player.hand):
        options = list(filter(lambda x: x.type() != 'Spades',c.validOptions(player.hand, cards_played[0].type(), spades_broke)))
        choice = options[0]
        for card in options:
            if card.number() > choice.number():
                card = choice
        card = choice
    else:
        usable_cards = [card for card in list(filter(lambda x: x != s.trick_winner(cards_played+[x]), c.validOptions(player.hand, cards_played[0].type(), spades_broke)))]

        if usable_cards == []:
            usable_cards = c.validOptions(player.hand, cards_played[0].type(),spades_broke)
            if len(cards_played) != 3:
                usable_cards.reverse()
        card = usable_cards[-1]
        
    return card
        
def take(player, cards_played):
    if len(cards_played) == 0:
        good_choices = list(filter(lambda x: x in winners(cardsLeft), c.validOptions(player.hand, None, spades_broke))) 
        if good_choices != []:
            card = good_choices[0]
        else:
            card = middle(c.validOptions(player.hand, None, spades_broke))
    elif len(cards_played) == 3:
        good_choices = list(filter(lambda x: x == s.trick_winner(cards_played+[x]), c.validOptions(player.hand, cards_played[0].type(), spades_broke)))
        if good_choices != []:
            card = good_choices[0]
        else:
            card = protect(player, cards_played)
    else:
        if s.trick_winner(cards_played).type() == 'Spades':
            good_choices = list(filter(lambda x: x == s.trick_winner(cards_played+[x]), c.validOptions(player.hand, cards_played[0].type(), spades_broke)))
        else:
            good_choices = list(filter(lambda x: x in winners(cardsLeft) and x == s.trick_winner(cards_played+[x]), c.validOptions(player.hand, cards_played[0].type(), spades_broke)))

        if good_choices != []:
            card = good_choices[0]

        elif c.numberInSuit(player.hand, cards_played[0].type()) == 0:
            options = cardsLeftInSuit(player.hand, 'Spades')
            if options != []:
                card = options[0]
            else:
                card = protect(player, cards_played)
        else:
            if middle(list(filter(lambda x: x == s.trick_winner(cards_played+[x]), c.validOptions(player.hand, cards_played[0].type(), spades_broke)))) == 'King':
                card = protect(player, cards_played)
            else:
                card = middle(list(filter(lambda x: x == s.trick_winner(cards_played+[x]), c.validOptions(player.hand, cards_played[0].type(), spades_broke))))
                if card is None:
                    card = protect(player, cards_played)
    return card

def protect(player, cards_played):
    if c.numberInSuit(player.hand, cards_played[0].type()) != 0:
        card = cardsLeftInSuit(player.hand,cards_played[0].type())[0]
    else:
        dumpable_cards = list(filter(lambda x: x not in winners(cardsLeft), c.validOptions(player.hand, cards_played[0].type(), False)))
        if dumpable_cards == []:
            dumpable_cards = c.validOptions(player.hand, cards_played[0].type(), False)
        choice = dumpable_cards[0]
        for card in dumpable_cards:
            if card.number() < choice.number():
                choice = card
        card = choice
    return card

def who_to_adjust(player):
    teammate = player.knowledge.teammate
    opponent1 = player.knowledge.opponent1
    opponent2 = player.knowledge.opponent2
    adjustment = 0
    considerations = list(filter(lambda x: x[0] != -1, [teammate, opponent1, opponent2]))
    for player in considerations:
        adjustment += adjust(player)
    return adjustment

def adjust(player):
    try:
        times = player_info[(player[7].lower(), str(player[8]), str(player[0]))][0]
        total = player_info[(player[7].lower(), str(player[8]), str(player[0]))][1]
        return int(total)/int(times) - player[0]
    except KeyError:
        return 0

#    for child in root:
#        if child.attrib['name'] == player[7].lower() and int(child.attrib['position']) == player[8]:
#            for bid in child:
#                if int(bid.attrib['contract']) == player[0]:
#                    return (int(bid[1].text)/int(bid[0].text) - int(player[0]))
#    return 0    

def bidding(player, bids):
    bid = trump(player.hand, 'Spades') + non_trump(player.hand, 'Clubs') + non_trump(player.hand, 'Hearts') + non_trump(player.hand, 'Diamonds')
    if sum(bids) + bid >= 13:
        bid += -1
        bid = max(bid, 1)
    elif 0 == player.knowledge.opponent1[0] or 0 == player.knowledge.opponent2[0]:
        bid += -1
        bid = max(bid, 0)
    elif 0 == player.knowledge.teammate[0]:
        bid += 1
    if bid == 0 and (c.Card('Ace', 'Spades') in player.hand or c.Card('King', 'Spades') in player.hand):
        bid += 1
    bid += who_to_adjust(player)
    return round(bid)


def trump(cards, suit):
    bid = 0
    options = [x.number() for x in cardsLeftInSuit(cards, suit)]
    if 'Ace' in options:
        bid += 1
        options.remove('Ace')
        if 'King' in options:
            bid += 1
            options.remove('King')
            if 'Queen' in options:
                bid += 1
                options.remove('Queen')
    elif 'King' in options and len(options) > 1:
        bid += 1
        options.remove('King')
        if 'Queen' in options and len(options) > 2:
            bid += 1
            options.remove('Queen')
    elif 'Queen' in options and len(options) > 2:
        bid += 1
        options.remove('Queen')
    bid += max([len(options) - 2,0])
    return bid

def non_trump(cards, suit):
    bid = 0
    options = [x.number() for x in cardsLeftInSuit(cards, suit)]
    if 'Ace' in options:
        bid += 1
    if 2 <= len(options) < 4 and 'King' in options:
        bid += .75
    if len(options) == 0:
        bid += 2
    if len(options) == 1:
        bid += 1
    return bid
