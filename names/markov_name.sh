#!/bin/bash

if [[ -f names.zip ]]
then
    echo What year would you like to sample from? You have from 1880 to 2012
    read answer
    year="yob${answer}.txt"
    unzip -p names.zip $year > test.txt
    'python' parser.py test.txt
    rm test.txt
else
    echo "You need to download the names file from the government. Would you like to do this? (y/n)"
    read answer
    if [[ $answer = y ]]
    then
	wget http://www.ssa.gov/oact/babynames/names.zip
	./markov_name.sh
    else
	echo Well then. I see how it is.
    fi
fi