#!/usr/bin/env python3.3
# Parses a text file with popular names

import random
import csv
import numpy as np
from sys import argv

# This reads through the csv file and and feeds the tokens to a function which builds the frequency matrix
def parser():
    input_file = argv[1]
    frequency_matrix = np.zeros( (27*26+1, 27) )
    csvfile = open(input_file)
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        frequency_matrix = add_freq(list(map(ord, row[0].lower())),int(row[2]), frequency_matrix)
    return frequency_matrix

# This actually fills in the frequency matrix. It currently has a frame of two, because I find the names to have the maximal combination of interestingness and readability
# This can pretty simply be changed to a different frame if desired
# The indices are created by having a numpy matrix, where the row indicates the seed, and the corresponding values correspond to the following letter or end
# These indices follow the pattern of the letter at the beginning of a name, and then what letters might follow that one
# It then loops through the alphabet, going "aa", "ab", ..., "az", "ba", "bb", ..., "zz"
def add_freq(word, number, matrix):
    matrix[0,word[0] - 97] += number
    matrix[word[0]-96,word[1]-97] += number
    matrix[26*(word[-2]-96) + word[-1] - 96,26] += number
    for i in range(1,len(word) - 1):
        matrix[26*(word[i-1]-96) + word[i] - 96, word[i+1] - 97] += number
    return matrix

# This takes a given seed and frequency matrix, and randomly picks a number less than the sum of the row correponding to that seed
# It then takes that number, and subtracts the column values from it successively, and when it reachs negatives, it returns that value.
# This takes the weighted distribution into account for randomness
def next_char(seed, matrix):
    next_term = random.randrange(np.sum(matrix[seed]))
    for column in range(27):
        next_term += -1*matrix[seed,column]
        if next_term.min() < 0:
            return column

# This creates a word, by randomly finding the first and second letters, and then from those two letters, it has a seed which it can find the next letter
# This process is repeated until an end character is returned. For more interest, I've disallowed two letter names
def create_word(matrix):
    word = []
    seeds = []
    seed_0 = next_char(0, matrix)+1
    seeds.append(seed_0)
    seed_1 = next_char(seed_0, matrix)+1
    seeds.append(seed_1)
    word.append(seed_0+96)
    word.append(seed_1+96)
    while seed_1 != 27:
        seed_1 = next_char(seeds[0]*26 + seeds[1], matrix)+1
        seeds[0] = seeds[1]
        seeds[1] = seed_1
        word.append(seed_1+96)
    word = word[0:len(word)-1]
    if len(word) > 2:
        print("".join(map(chr,word)))
    else:
        create_word(matrix)

create_word(parser())
