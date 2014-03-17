#!/usr/bin/env python3.3
# tests the card game library
# -*- coding: utf-8 -*-

import cardgames as c
import numbers_to_words as NW
import os
from termcolor import colored
import spades_AI as AI
#import xml.etree.ElementTree as ET
import pickle
from itertools import product

cardsLeft = []

# From the random deck, creates four hands, sorts them, and returns them in a list
def create_hands():
    deck = c.Deck().deck
    hands = []
    for i in range(4):
        hand = deck[13*i:(1+i)*13]
        hand.sort()
        hands.append(hand)
    return hands

# Changes the global variable spades to broken
def break_spades():
    global spades_broken
    spades_broken = True

# Lets the player pick a suit to play if able, otherwise, does not
def suit_choice_human(hand, restriction):
    if (restriction == None) or c.numberInSuit(hand, restriction)==0:
        while True:
            print("\nWhich suit would you like to play?")
            suit_options = {}
            choices = [suit for suit in c.Card.SUITS if c.numberInSuit(hand, suit) != 0]
            for suit in choices:
                print("({}). {}".format(suit[0], suit))
            ans = input("-> ").lower().strip()

            if ans in ['c','d','h','s']:
                ans = c.Card.SUIT_ALIAS[ans].lower()

            if ans =='clubs' and c.numberInSuit(hand, 'Clubs')!= 0:
                return card_choice_human('Clubs', hand)
                break
            elif ans == 'diamonds' and c.numberInSuit(hand, 'Diamonds')!=0:
                return card_choice_human('Diamonds', hand)
                break
            elif ans =='hearts' and c.numberInSuit(hand, 'Hearts') != 0:
                return card_choice_human('Hearts', hand)
                break
            elif ans== 'spades' and c.numberInSuit(hand, 'Spades') != 0:
                if (spades_broken == True) or (c.numberInSuit(hand, restriction)==0 and restriction != None) or (c.numberInSuit(hand, 'Hearts') == c.numberInSuit(hand, 'Diamonds') == c.numberInSuit(hand, 'Clubs')==0):
                    return card_choice_human('Spades', hand)
                    break
                else:
                    print("Spades has not been broken yet, you can't play that. Try again")
            else:
                print("Sorry, that is not a legal move. Please try again.")
    else:
        return card_choice_human(restriction, hand)

# Given a hand, and a specific suit, offers a choice of which card to play
def card_choice_human(suit, hand):
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
            ans = c.Card.ALIASES[ans]
        else:
            print("That is invalid input. Please try again.")
            ans = input("-> ").lower().strip().capitalize()
    return(c.Card(suit, ans))
    

# Plays through a trick until four cards have been played, while keeping the restrictions
def trick_play(hand, cards_played):
    if len(cards_played) != 0:
        choice = suit_choice_human(hand, ((cards_played)[0]).type())
        cards_played.append(choice)
        return cards_played
    else:
        choice = suit_choice_human(hand, None)
        cards_played.append(choice)
        return cards_played

# Finds the highest card in the trick
def trick_winner(cards_played):
    # This saves time by only calling it once
    card = c.highestInSuit(cards_played, 'Spades', spades_broken)
    if card != None:
        return card
    else:
        return c.highestInSuit(cards_played, cards_played[0].type(), spades_broken)

# Goes through each of the players and lets them bid
# Returns a list of bids made
def bidding(players):
    bids = [-1,-1,-1,-1]
    for i in range(4):
        if players[i].isAI:
            bids[i] = AI.bidding(players[i], bids)
        else:
            print("{} \t {}".format(players[0].team, players[1].team))

            # This will show all previous bids
            for n in range(i):
                print("{} bid {}".format(players[n].name, bids[n]))
            bids[i] = bidding_human(players[i], bids[0:i])
            clear()
            input("Press Enter to continue")
            clear()
        players[i].knowledge.cards_left = cardsLeft
        players[(i+2)%4].knowledge.teammate = [bids[i],[], False, False, False, False, 0,players[i].name,i]
        players[(i+1)%4].knowledge.opponent1 = [bids[i],[], False, False, False, False, 0,players[i].name,i]
        players[(i-1)%4].knowledge.opponent2 = [bids[i],[], False, False, False, False, 0,players[i].name,i]
        players[i].contract = bids[i]
        players[i].lastTrick = None
    return players

def bidding_human(player, bids):
#    print("There are {} bags on the table".format(13 - sum(bids)))
    print("\nYour hand is:")
    print(", ".join(map(str, player.hand)))
    print("\n{}, what would you like to bid?".format(player.name))
    while True:
        ans = input('-> ').strip()
        try:
            int(ans)
            if bid_check(int(ans)):
                bid = int(ans)
                break
        except ValueError: # Ensures that the input will not break
            if ans.lower() == 'nil' or ans == "#YOLO":
                bid = 0
                break
            elif NW.words_to_number(ans) != None:
                bid = NW.words_to_number(ans)
                if bid_check(bid):
                    break
                else:
                    print("Sorry, I don't recognize that input. Type a number, or write 'nil'")
    return bid

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

# This will play through an entire trick
def entire_trick(players):
    global cardsLeft
    cards_played = []
#    test = players
    for player in players:
        if player.isAI:
            cards_played = AI.move(player, cards_played, spades_broken)
        else:
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

            cards_played = trick_play(player.hand, cards_played)
            clear()
            input("Press Enter to continue")
            clear()
        if cards_played[-1].type() == 'Spades':
            break_spades()
        (player.hand).remove(cards_played[-1])
    lead_suit = cards_played[0].type()
    for card in cards_played:
        cardsLeft.remove(card)
    winner = trick_winner(cards_played)
    index = cards_played.index(winner)
    for i in range(4):
        if (cards_played[(i+1)%4].type() != lead_suit):
            players[i].knowledge.opponent2[2 + c.Card.SUITS.index(lead_suit)] = True
            players[(i-1)%4].knowledge.teammate[2 + c.Card.SUITS.index(lead_suit)] = True
            players[(i+2)%4].knowledge.opponent1[2 + c.Card.SUITS.index(lead_suit)] = True

        players[i].lastTrick = cards_played[i]
        players[i].knowledge.cards_left = cardsLeft
        players[i].knowledge.teammate[1].append(cards_played[(i+2)%4])
        players[i].knowledge.opponent1[1].append(cards_played[(i-1)%4])
        players[i].knowledge.opponent2[1].append(cards_played[(i+1)%4])
        
    players[(index+1)%4].knowledge.opponent1[5] += 1
    players[(index-1)%4].knowledge.opponent2[5] += 1
    players[(index+2)%4].knowledge.teammate[5] += 1
#    winner = trick_winner(cards_played)
# Makes it so that the winner of the trick leads play
    index = cards_played.index(winner)
    players[index].tricks += 1
    return index

def move_AI(player, cards_played, spades_broken):
    if len(cards_played) == 0:
        return [c.validOptions(player.hand, None, spades_broken)[-1]]
    else:
        cards_played.append(c.validOptions(player.hand, cards_played[0].type(), spades_broken)[-1])
        return cards_played

def play_hand(players):
#    tree = ET.parse('players.xml')
#    root = tree.getroot()
#    elements = [(x.attrib['name'],x.attrib['position'], [y.attrib['contract'] for y in x]) for x in root]
#    combinations_intermediate = [product([(x[0],x[1])],x[2]) for x in elements]
#    combinations = [item for sublist in combinations_intermediate for item in sublist]
#    partial_elements = [x[0] for x in combinations]
    try:
        player_info = pickle.load(open("players.p", "rb"))
    except FileNotFoundError:
        player_info = {}
        pickle.dump(player_info, open("players.p","wb"))
    original_seats = players
#    for x in combinations:
#        print(x)
#    for x in partial_elements:
#        print(x)
    clear()
    global cardsLeft
    global spades_broken
    cardsLeft = c.Deck().deck
    cardsLeft.sort()
    spades_broken = False
    players = bidding(players)
    for i in range(13):
        index = entire_trick(players)
        players = rotate(players, index)
#    print("The last trick was:")
#    print(", ".join(map(str, cards_played)))
    for player in players:
        print("{} bid {} and took {} tricks.".format(player.name, player.contract, player.tricks))
        try:
            player_info[(player.name, str(original_seats.index(player)), str(player.contract))][0] += 1
            player_info[(player.name, str(original_seats.index(player)), str(player.contract))][1] += player.tricks
        except KeyError:
            player_info[(player.name, str(original_seats.index(player)), str(player.contract))] = [1,player.tricks]
#            player_info[(player.name, str(original_seats.index(player)), str(player.contract))][1] = player.tricks
        pickle.dump(player_info, open("players.p", "wb"))
#        if ((player.name, str(original_seats.index(player))),str(player.contract)) in combinations:
#            print(1)
#            for child in root:
#                if child.attrib['name'] == player.name and child.attrib['position']==str(original_seats.index(player)):
#                    for bid in child:
#                        print(4)
#                        if bid.attrib['contract'] == player.contract:
#                            bid[0] = int(bid[0]) + 1
#                            bid[1] = int(bid[1]) + player.tricks
#                            ElementTree().write('players.xml')
#                            break
#                    break
#        elif (player.name, str(original_seats.index(player))) in partial_elements:
#            print(2)
#            for child in root:
#                if child.attrib['name'] == player.name and child.attrib['position']==str(original_seats.index(player)):
#                    print(3)
#                    bid = ET.SubElement(child, "bid")
 #                   bid.set("contract",str(player.contract))
 #                   times = ET.SubElement(bid, "times")
 #                   total_tricks = ET.SubElement(bid, "total_tricks")
 #                   times.text = "1"
  #                  total_tricks.text = str(player.tricks)
  #                  ET.ElementTree().write('players.xml')
   #                 break
    #    else:
     #       pass
#    tree.write('players.xml')
                            

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

def end_game(teams):
    winner = teams[0] if teams[0].score > teams[1].score else teams[1]
    teams.remove(winner)
    loser = teams[0]
    print("{} win with a score of {}!".format(winner.name, winner.score))
    print("{} lose with a score of {}".format(loser.name, loser.score))
                      
