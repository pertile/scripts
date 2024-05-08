import numpy

list = []
with open('english.txt') as file:
    lines = file.readlines()
    for line in lines:
        fields = line.split("\t")
        list.append({
            "present": fields[0],
            "past": fields[1].split(","),
            "spanish": fields[2].split(","),
        })



questions = 10

options = numpy.random.choice(list, questions, False)
# print(option)

right = 0
wrong = 0

for option in options:
    print(f"Which is the past for {option['present']}?")
    answer = input()

    this_wrong = 0
    while answer not in option['past'] and this_wrong <= 3:
        wrong = wrong + 1
        this_wrong = this_wrong + 1
        print("You are wrong! Try again")
        answer = input()

    if  answer in option['past']:
        right = right + 1
        print("You are right!")
    else:
        print(f"Correct answer is {option['past']}")

points = (1 - wrong / (wrong + questions)) * 100
print(f"You made {wrong} wrong answers in {questions} questions. You have a {points} %.")
if points > 70:
    print("You are approved!")
else:
    print("You failed. You have to study more.")