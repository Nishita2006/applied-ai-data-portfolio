#Python calculator
operator = input("Select the operation you would like to perform(+, - , *, /):")
num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))
if operator == "+":
    print(num1 + num2)
elif operator == "-":
    print(num1 - num2)
elif operator == "*":
    print(num1 * num2)
elif operator == "/" and num2 == 0:
    print("Error: Cannot divide by zero")
elif operator == "/" :
    print(num1 / num2)
else:
    print("invalid operator")