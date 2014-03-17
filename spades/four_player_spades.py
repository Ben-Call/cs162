#!/usr/bin/env python3.3
# tests the card game library
# -*- coding: utf-8 -*-

import cardgames
import numbers_to_words as NW
import os
from termcolor import colored

spades_broken = False
blahdeck = cardgames.Deck()

# From the random deck, creates four hands, sorts them, and returns them in a list
def create_hands():
    deck = cardgames.Deck().deck
    hands = []
    for i in range(4):
        hand = deck[13*i:(1+i)*13]
        hand.sort()
        hands.append(hand)
    return hands

# Provides a player object with multiple attributes
class Player(object):
    def __init__(self, name, hand, tricks, contract, score, team, lastTrick):
        self.name = str(name)
        self.hand = hand
        self.tricks = int(tricks)
        self.contract = int(contract)
        self.score = int(score)
        self.team = team
        self.lastTrick = lastTrick

    def __str__(self):
        return "{} bid {} and took {} tricks".format(self.name, self.contract, self.tricks)

    def __repr__(self):
        return str([self.name, self.hand, self.tricks, self.contract, self.team, self.lastTrick])

# Creates a team object
class Team(object):
    def __init__(self, name, player1, player2, score):
        self.name = str(name)
        self.player1 = player1
        self.player2 = player2
        self.score = int(score)

    def __str__(self):
        return "{} has a score of {}".format(self.name, self.score)

    def __repr__(self):
        return str([self.name, self.player1, self.player2, self.score])

# Provides the total team contract
    def contract(self):
        return (self.player1.contract + self.player2.contract)

#Provides the total number of tricks taken
    def tricks(self):
        return (self.player1.tricks + self.player2.tricks)

# Determines if a hand is void in a suit
def isVoid(hand, suit):
    if suit not in [card.type() for card in hand]:
        return True
    else:
        return False

# Changes the global variable spades to broken
def break_spades():
    global spades_broken
    spades_broken = True

# Lets the player pick a suit to play if able, otherwise, does not
def suit_choice(hand, restriction, spades_broken):
    if (restriction == None) or isVoid(hand, restriction):
        while True:
            print("\nWhich suit would you like to play?")
            suit_options = {}
            choices = [suit for suit in cardgames.Card.SUITS if not isVoid(hand, suit)]
            for suit in choices:
                print("({}). {}".format(suit[0], suit))
            ans = input("-> ").lower().strip()

            if ans in ['c','d','h','s']:
                ans = cardgames.Card.SUIT_ALIAS[ans].lower()

            if ans =='clubs' and not isVoid(hand, 'Clubs'):
                return card_choice('Clubs', hand)
                break
            elif ans == 'diamonds' and not isVoid(hand, 'Diamonds'):
                return card_choice('Diamonds', hand)
                break
            elif ans =='hearts' and not isVoid(hand, 'Hearts'):
                return card_choice('Hearts', hand)
                break
            elif ans== 'spades' and not isVoid(hand, 'Spades'):
                if (spades_broken == True) or (isVoid(hand, restriction) and restriction != None) or (isVoid(hand, 'Hearts') and isVoid(hand, 'Diamonds') and isVoid(hand, 'Clubs')):
                    break_spades()
                    return card_choice('Spades', hand)
                    break
                else:
                    print("Spades has not been broken yet, you can't play that. Try again")
            else:
                print("Sorry, that is not a legal move. Please try again.")
    else:
        return card_choice(restriction, hand)

# Given a hand, and a specific suit, offers a choice of which card to play
def card_choice(suit, hand):
    choices = [x.number() for x in filter(lambda x: suit==x.type(), hand)]
    print("\nWhich card would you like to play? Please type the value of the card.")
    for value in choices:
        print('{}'.format(value))
    ans = str(input("-> ")).lower().strip().capitalize()
    while True:
        if ans in choices:
            break
        elif str(NW.words_to_number(ans)) in choices:
            ans = str(NW.words_to_number(ans))
            break
        elif ans in ['A','K','Q','J']:
            ans = cardgames.Card.ALIASES[ans]
        else:
            print("That is invalid input. Please try again.")
            ans = input("-> ").lower().strip().capitalize()
    return(cardgames.Card(suit, ans))
 
# Plays through a trick until four cards have been played, while keeping the restrictions
def trick_play(hand, cards_played, spades_broken):
    if len(cards_played) != 0:
        choice = suit_choice(hand, ((cards_played)[0]).type(), spades_broken)
        cards_played.append(choice)
        return cards_played
    else:
        choice = suit_choice(hand, None, spades_broken)
        cards_played.append(choice)
        return cards_played

# Determines the highest card in a specific suit, returning None if there are no possibilites
def highest_in_suit(suit, cards):
    valid_cards = [card for card in filter(lambda x: suit==x.type(),cards)]
    if valid_cards == []:
        return None
    else:
        valid_cards.sort()
        return valid_cards[-1]

# Finds the highest card in the trick
def trick_winner(cards_played):
    # This saves time by only calling it once
    card = highest_in_suit('Spades', cards_played)
    if card != None:
        return card
    else:
        return highest_in_suit(cards_played[0].type(), cards_played)

# Goes through each of the players and lets them bid
# Returns a list of bids made
def bidding(players):
    bids = []
    for player in players:
        print("{} \t {}".format(players[0].team, players[1].team))

# This will show all previous bids
        for i in range(len(bids)):
            print("{} bid {}".format(players[i].name, bids[i]))
        print("There are {} bags on the table".format(13 - sum(bids)))
        print("\nYour hand is:")
        print(", ".join(map(str, player.hand)))
        print("\n{}, what would you like to bid?".format(player.name))
        while True:
            ans = input('-> ').strip()
            try:
                int(ans)
                if bid_check(int(ans)):
                    ans = int(ans)
                    break
            except ValueError: # Ensures that the input will not break
                if ans.lower() == 'nil':
                    ans = 0
                    break
                elif NW.words_to_number(ans) != None:
                    ans = NW.words_to_number(ans)
                    if bid_check(ans):
                        break
                else:
                    print("Sorry, I don't recognize that input. Type a number, or write 'nil'")
        bids.append(ans)
        clear()
        input("Press Enter to continue")
        clear()
    return bids

# Returns false and an error message when an impossible bid is made
def bid_check(bid):
    if bid > 13:
        print("That bid is ... inadvisable. Try again")
        return False
    elif bid < 0:
        print("I think you might be a little too confident here.")
        return False
    else:
        return True

# Rotates the list of players by an index to account for change in play rotation
def rotate(players, index):
    rotation = [(i + index)%len(players) for i in range(len(players))]
    new_players = [players[i] for i in rotation]
    return new_players


def create_players():
    players = []
    for i in range(4):
        name = str(input("What is your name? "))
        if name == "":
            name = str(i+1)
        player = Player(name, [],0,0,i+1, "No team yet", None)
        players.append(player)
    return players

# This will play through an entire trick
def entire_trick(players):
    cards_played = []
    for player in players:
        teammate = players[(players.index(player)+2)%4]
        print("=================================================================================")
        print("***                         {0: >15}'s turn                            ***".format(player.name))
        print("=================================================================================")
        print("Player          Contract   Tricks   Card played on last trick")
        print("------          --------   -------   -------------------------")

        for i in players:
            print("{0: <15}    {1: <2}         {2: <2}              {3}".format(i.name, i.contract, i.tricks, i.lastTrick))

        print("----------------------------------------------------------------")

# If one person on your team bids nil, the contracts work differently; this reflects that
        if (player.contract != 0 and teammate.contract == 0) or player.contract == 0:
                print("Your contract is {} and you've taken {} tricks so far\n".format(player.contract, player.tricks))
        else:
                print("Your team contract is {} and collectively you've taken {} tricks so far".format(player.contract + teammate.contract, player.tricks + teammate.tricks))

        print("\nYour hand is:")
        print(", ".join(map(str, player.hand)))

        if len(cards_played) != 0:
            print("\nThe cards played so far have been:")
            print(", ".join(map(str, cards_played)))

        cards_played = trick_play(player.hand, cards_played, spades_broken)
        (player.hand).remove(cards_played[-1])
        clear()
        input("Press Enter to continue")
        clear()

    for i in range(4):
        players[i].lastTrick = cards_played[i]
    winner = trick_winner(cards_played)
# Makes it so that the winner of the trick leads play
    index = cards_played.index(winner)
    players[index].tricks += 1
    return index

def play_hand(players):
    clear()
    bids = bidding(players)
    for i in range(4):
        players[i].contract = bids[i]
    for i in range(13):
        index = entire_trick(players)
        players = rotate(players, index)
    for player in players:
        print(player)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def scores(teams):
    for team in teams:
        bags = abs(team.score) % 10
        if team.player1.contract == 0:
            team.score += nil_scoring(team.player1, team.player2, bags)
        elif team.player2.contract == 0:
            team.score += nil_scoring(team.player2, team.player1, bags)
        else:
            if team.tricks() < team.contract():
                team.score += (-10)*team.contract()
            else:
                team.score += 10 *team.contract() + (team.tricks() - team.contract())
                if team.tricks() - team.contract() + bags >= 10:
                    team.score += -100

def nil_scoring(nil, non_nil, bags):
    score = 0
    if nil.tricks == 0:
        score += 100
    else:
        score += -100
    if non_nil.tricks < non_nil.contract:
        score += (-10)*(non_nil.contract)
    else:
        score += (10 * non_nil.contract) + (non_nil.tricks - non_nil.contract)
        if non_nil.tricks - non_nil.contract + bags >= 10:
                score += -100
    return score

def create_teams(players):
    teams = []
    for i in range(2):
        name = input("{} and {}, what do you want your team name to be? ".format(players[i].name, players[i+2].name))
        if name == "":
            name = str(i+1)
        teams.append(Team(name,players[i],players[i+2],0))
    return teams

def play_game():
    orig_players = create_players()
    deal = -1
    teams = create_teams(orig_players)
    for i in range(4):
        orig_players[i].team = teams[i%2]

    while ((orig_players[0].score < 100 and orig_players[1].score < 100) or (orig_players[0].score == orig_players[1].score)):
        deal += 1
        players = rotate(orig_players,(deal%4))
        hands = create_hands()
        for i in range(4):
            players[i].hand = hands[i]
            players[i].score = teams[i%2].score
            players[i].tricks = 0
#        print("Team {} score is: {} points".format(orig_players[0].name, orig_players[0].score))
#        print("Team {} score is: {} points".format(orig_players[1].name, orig_players[1].score))
        print("{}\n{}".format(teams[0],teams[1]))
        input("Press Enter to continue")
        play_hand(players)
        scores(teams)
    end_game(teams)

def end_game(teams):
    print("{} wins with a score of {}!".format(max(teams).name, max(teams).score))
    print("{} loses with a score of {}".format(min(teams).name, min(teams).score))
                      
clear()
play_game()
