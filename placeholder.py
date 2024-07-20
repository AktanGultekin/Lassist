import re

#regex = r"George"
regex = [r"George", r"Georgie", r"george", 
r"georgie", r"Vanessa", r"met$", r"met$", r"gül$"]

"""lines = input("Say something: ") # Voice processed lines """

lines =  ["Hi, I'm Grayson, George", "Hi, I'm George", "Hi, I'm Georgie", "Hi, I'm Grayson, Georgie", "Hi, I'm Grayson, Vanessa"]
string = """Hi! I'm George. I want to rent a room to my family for a month. She, Vanessa, plays violin. So it may be disturb neighbours. We are so sorry about it. 
Ben Ahmet. Bu da kızım Ayşegül"""


print(re.findall(r'[Aa]yşegül', string))

print("\n")

for line in lines:
    print("\n")
    for single_regex in regex:
        if re.search(single_regex, line):
            print(f"Matched! Expected Name: {single_regex}\t\tGiven line : {line}")
        else:
            print(f"Not Matched! Expected Name: {single_regex}\t\tGiven line: {line}")

print("\n")

for single in regex:
    if re.search(single, string):
        print(f"Matched! Expected Name: {single}")
    else:
        print(f"Not Matched! Expected Name: {single}")




