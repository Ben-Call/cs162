#!/usr/bin/env python3.3
# Provides logic for the game's AI
# -*- coding: utf-8 -*-

import cardgames as c
import spades_engine as s
import pickle
import math

# This makes sure that a players.p file exists, and if it does not, it creates one
try:
    player_info = pickle.load(open("players.p", "rb"))
except FileNotFoundError:
    player_info = {}
    pickle.dump(player_info, open("players.p", "wb"))

# This variable makes it such that the AI functions do not need to get whether or not spade has been broken passed unneccessarily
spades_broke = False

# This returns the middle element of a list, rounded down
def middle(myList):
    if myList == []:
        return None
    else:
        return myList[math.ceil(len(myList)/2) - 1]

# This returns a list of cards that are left in a suit from a given collection
def cardsLeftInSuit(cards, suit):
    return list(filter(lambda x: x.type() == suit, cards))

# This takes a collection of cards, and returns a list of the highest one in each suit
def winners(deck):
    winners = []
    for suit in c.Card.SUITS:
        options = cardsLeftInSuit(cardsLeft, suit)
        if options != []:
            winners.append(options[-1])
    return winners

# This takes a player, the cards played so far in the trick, and whether spades has been broken
# If spades has been broken, then it will change the global variable in this module accordingly
# It returns a list of the cards played in the trick with it's choice appended
def move(player, cards_played, spades_broken):
    global spades_broke
    spades_broke = spades_broken
    card = decide_move(player, cards_played)
    cards_played.append(card)
    return cards_played

# Given a player's knowledge, it changes the cards left in the deck, and determines whether or not to protect the partner, try to take a trick, to dump cards, or to set a nil
# It returns the card chosen
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

# This is what a player will do if nothing else was triggered in the previous chain
# It also determines that if there are two or fewer bags on the table, the AI will always go for a neg
# It returns the card chosen
def normal_move(player, cards_played):
    if player.contract == 0 and player.tricks == 0:
        card= dump(player, cards_played)
    elif player.contract + player.knowledge.teammate[0] + player.knowledge.opponent1[0] + player.knowledge.opponent2[0] > 10 or player.contract > player.tricks:
        if len(cards_played) == 3 and s.trick_winner(cards_played) == cards_played[1] and player.knowledge.teammate[0] < player.knowledge.teammate[6]:
            card = protect(player, cards_played)
        elif len(cards_played) == 2 and s.trick_winner(cards_played) == cards_played[0] in winners(cardsLeft) and c.numberInSuit(cardsLeft, cards_played[0].type()) - c.numberInSuit(player.hand, cards_played[0].type()) >= 3:
            card = protect(player, cards_played)
        else:
            card = take(player, cards_played)            
    else:
       card = dump(player, cards_played)
    return card

# This is how the AI determines the best way to protect a partner nil
# It will play its winners, dump its lowest cards when their partner is protected, and play into their partners voids
# It will also run down spades when it has the option
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

# This is the criteria for what card to get rid of, given a player, and the cads played
# When leading, it will dump its lowest in the longest suit left so as to ensure somebody else takes it
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
        for suit in usable_suits:
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
        
# This determines the best way to take a trick, which means not playing what will in the future become a winner, and instead protecting with something lower
# This returns a card
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

# This returns what card a player will play in order to protect one of his or her winners from losing
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

# This takes a player, and based off of his knowledge, the AI determines if it needs to adjust based off of his bid
# If it sees -1 as a bid, it knows that that player has not bid yet, and it ignores it
# It returns the number of tricks the computer needs to adjust by
def who_to_adjust(player):
    teammate = player.knowledge.teammate
    opponent1 = player.knowledge.opponent1
    opponent2 = player.knowledge.opponent2
    adjustment = 0
    considerations = list(filter(lambda x: x[0] != -1, [teammate, opponent1, opponent2]))
    for player in considerations:
        adjustment += adjust(player)
    return adjustment

# Given a "player", which is really just the knowledge of the AI about this player, it determines if there is enough past bidding history
# to make a valid adjustment. In order to do this, the player must not have bid nil, and must have bid this number from this seat more than
# five times. If it does not meet these conditions, the AI makes no adjustment
def adjust(player):
    try:
        times = player_info[(player[7].lower(), str(player[8]), str(player[0]))][0]
        total = player_info[(player[7].lower(), str(player[8]), str(player[0]))][1]
        if int(times) > 5 and player[0] != 0:
            return int(total)/int(times) - player[0]
        else:
            return 0
    except KeyError:
        return 0

# This simply adds up the tricks in each suit according to some algorithms
# This also controls according to what else has been bid and adjusts up or down accordingly
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
    if bid == 0 and (c.Card('Spades', 'Ace') in player.hand or c.Card('Spades', 'King') in player.hand):
        bid += 1
    bid += who_to_adjust(player)
    return round(bid)

# This takes a collection of cards, and the suit (in case people want to extend this to something other than spades) and returns a number of tricks possible to take
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

# This returns the number of tricks it is possible to take given a collection of cards in a given non-trump suit
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
