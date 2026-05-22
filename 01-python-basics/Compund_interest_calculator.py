#Compound interest calculator
principle = float(input("Enter the principle amount: "))

while principle <= 0:
    print("Principle amount cannot be zero or Negative!")
    principle = float(input("Enter the principle amount: "))

interest_rate = float(input("Enter the interest rate: "))

while interest_rate <= 0:
    print("Interest rate cannot be zero or Negative!")
    interest_rate = float(input("Enter the interest rate: "))

time= float(input("Enter the time(yrs): "))

while time <= 0:
    print("time cannot be zero or Negative!")
    time = float(input("Enter the time(yrs): "))

total_balance = principle * (1 + (interest_rate/100)) ** time
total_balance = round(total_balance, 2)
print(f"Your total balance after {time} years with an interest rate of {interest_rate}% on principle amount {principle} is ${total_balance:.2f}")



