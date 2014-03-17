import spades_engine as s
import cardgames as c
import numbers_to_words as NW

smurfs = 0
masters = 0

def player_check(num):
    if num > 4 or num < 0:
        print("Please pick a number between 1 and 4")
        return False
    else:
        return True

def human_players():
    while True:
        num = input("How many players are human? Note, the default is to be on different teams. ")
        try:
            num = int(num)
            if player_check(num):
                break
            else:
                pass
        except ValueError:
            num = NW.words_to_number(num)
            if (num is not None) and player_check(num):
                break
            else:
                pass
    return num

def create_players():
    names = ["Hal", "Deep Thought", "GLADYS", "Skynet"]
    num = human_players()
    players = []
    for i in range(num):
        name = input("What is your name? ")
        if name == "":
            name = str(i+1)
        player = c.Player(name, [], 0, 0,0, "No team yet", None, False, c.Knowledge([], [-1], [-1], [-1]))
        players.append(player)
    for i in range(4 - num):
        player = c.Player(names[i], [], 0, 0, 0, "No team yet", None, True, c.Knowledge([], [-1], [-1], [-1]))
        players.append(player)
    return players

def create_teams(players):
    teams = [c.Team("The Smurfs", players[0], players[2], 0), c.Team("Masters of the Universe", players[1], players[3], 0)]
    print("{} and {}, you are on {}".format(players[0].name,players[2].name,teams[0].name))
    print("{} and {}, you are on {}".format(players[1].name,players[3].name,teams[1].name))
    return teams

def play_game():
    global smurfs
    global masters
    orig_players = create_players()
    deal = -1
    teams = create_teams(orig_players)
    input("Press Enter to continue")
    for i in range(4):
        orig_players[i].team = teams[i%2]

    while ((-300 < teams[0].score < 300 and -300 < teams[1].score < 300) or (teams[0].score == teams[1].score)):
         deal += 1
         players = s.rotate(orig_players,(deal%4))
         hands = s.create_hands()
         for i in range(4):
             players[i].hand = hands[i]
             players[i].score = teams[i%2].score
             players[i].tricks = 0
#         print("{}\n{}".format(teams[0],teams[1]))
         s.play_hand(players)
         s.scores(teams)
         print("{}\n{}".format(teams[0],teams[1]))
         ans = input("It is now {}'s turn. Press Enter to continue".format(players[1].name))
         if ans.lower() == "#debug":
             for i in range(4):
                 print(", ".join(map(str, hands[i])))
             print("Is there a problem?")
             input("Press Enter to continue")
    s.end_game(teams)

s.clear()
play_game()
