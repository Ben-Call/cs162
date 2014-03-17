#numbers that add to multiplier
tens = dict(zip(['twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety'],range(20,100,10)))
teens = dict(zip(['ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen'],range(10,20)))
ones = dict(zip(['one','two','three','four','five','six','seven','eight','nine'],range(1,10)))

# numbers multiply by multiplier
hundreds = {'hundred':100}
big = {"thousand":1000, "million":1000000, "billion":1000000000, "trillion":1000000000000, "quadrillion":1000000000000000, "quintillion":1000000000000000, "sextillion":1000000000000000000} # also resets multiplier

def words_to_number(words):
    multiplier = 0
    total = 0
    # Added a slight modification that allowed case-matching
    for word in words.lower().replace("-"," ").replace(",","").replace("and","").split(): # fixes format of all valid ways to input words
        if word in ones:
            multiplier+=ones[word]
        elif word in tens:
            multiplier+=tens[word]
        elif word in teens:
            multiplier+=teens[word]
        elif word in hundreds:
            multiplier*=hundreds[word]
        elif word in big:
            total += multiplier*big[word]
            multiplier=0
        else: # ignores invalid input (for now; this can be easily fixed later)
            return None # To make it easy to identify
    total += multiplier # add numbers left in multiplier
    return(total)
