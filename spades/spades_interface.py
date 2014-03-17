import spades_engine as s
import cardgames as c
import numbers_to_words as NW

# This ensures that only a valid number of players is playing
# 0 is allowed for debugging purposes and because it's fun to watch the AI battle
def player_check(num):
    if num > 4 or num < 0:
        print("Please pick a number between 1 and 4")
        return False
    else:
        return True

# This prompts the user for how many human players there are.
# After checking to make sure the input is a number and is reasonable, it returns that number
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

# Creates the human and AI players with their base information
# This includes the base knowledge that they have, with -1 indicating it is the beginning of a hand
def create_players():
    names = ["Hal", "Deep Thought", "GLaDOS", "Skynet"]
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

# This creates the teams, and assigns them players
# It is very easy to allow user input to determine team names, but I enjoy these instead
def create_teams(players):
    teams = [c.Team("The Smurfs", players[0], players[2], 0), c.Team("Masters of the Universe", players[1], players[3], 0)]
    print("{} and {}, you are on {}".format(players[0].name,players[2].name,teams[0].name))
    print("{} and {}, you are on {}".format(players[1].name,players[3].name,teams[1].name))
    return teams


# This will play through a game of spades, calling the play_hand function repeatedly with new hands until someone wins
# Because of the rotating nature of dealing and leading, this is kept track of with the variable deal
# The function rotate is used to permute the order of the original players accordingly, since that is not carried in the player class
# A debug mode is included if something seem off with the gameplay on the last hand. Rather then pressing enter, you type #DEBUG
def play_game():
    orig_players = create_players()
    deal = -1
    teams = create_teams(orig_players)
    input("Press Enter to continue")
    hands = s.create_hands()

    for i in range(4):
        orig_players[i].team = teams[i%2]

    while ((-500 < teams[0].score < 500 and -500 < teams[1].score < 500) or (teams[0].score == teams[1].score)):
         deal += 1
         players = s.rotate(orig_players,(deal%4))
         old_hands = hands
         hands = s.create_hands()
         print("{}\n{}".format(teams[0],teams[1]))
         ans = input("It is now {}'s turn. Press Enter to continue".format(players[0].name))

         if ans.lower() == "#debug":
             for i in range(4):
                 print(", ".join(map(str, hands[i])))
             print("Is there a problem?")
             input("Press Enter to continue")

         for i in range(4):
             players[i].hand = hands[i]
             players[i].score = teams[i%2].score
             players[i].tricks = 0

         s.play_hand(players)
         s.scores(teams)
    s.end_game(teams)

# This clears the terminal screen, and then plays the game
s.clear()
play_game()
