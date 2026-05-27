# Quiz game
import time
questions = ("How many elements are in the periodic table?: ",
             "Which animal lays the largest eggs?: ",
             "What is the most abundant gas in Earth's atmosphere?: ",
             "How many bones are in the human body?: ",
             "Which planet in the solar system is the hottest?: ")

options = (("A. 116", "B. 117", "C. 118", "D. 119"),
           ("A. Whale", "B. Crocodile", "C. Elephant", "D. Ostrich"),
           ("A. Nitrogen", "B. Oxygen", "C. Carbon-Dioxide", "D. Hydrogen"),
           ("A. 206", "B. 207", "C. 208", "D. 209"),
           ("A. Mercury", "B. Venus", "C. Earth", "D. Mars"),)

answers = ("C", "D", "A", "A", "B")

guesses = []  # List to store all user answers. A tuple would not work because tuples are immutable.
score = 0
for question in range(len(questions)):
    print("-------------------------------------------------")
    print(questions[question])
    for option in options[question]:
        print(option)

    guess = input("\nWhat is your answer to the above question? ")
    guess = guess.strip().upper() # strip() so that extra spaces from user input don't make a difference
    while guess not in ["A","B","C","D"]:
        print("Please pick an answer from the given options")
        guess = input("\nWhat is your answer to the above question? ")
        guess = guess.strip().upper() 
    guesses.append(guess)
    if guess == answers[question]:
        print("Your answer is correct!!")
        score +=1
        print()
    else:
        print("Incorrect answer!")
        print(f"The correct answer is {answers[question]}")
        print()

print("Calculating your score...")
time.sleep(2)

print(f"Your score for this quiz is {score}/{len(questions)}")
print()
print(f"Your guesses were {guesses}")
print(f"The correct answers were {list(answers)}")