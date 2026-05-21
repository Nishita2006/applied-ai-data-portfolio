#Weight converter
unit = input("Enter a unit(kilograms or pounds):")
unit = unit.lower()
weight = float(input("Enter a weight:"))
if weight < 0:
    print("Enter value for weight is invalid")
elif unit == "pounds":
    kilograms = weight * 0.4536
    kilograms = round(kilograms, 2)
    print(f"{weight} lb = {kilograms} kg")
elif unit == "kilograms":
    pounds = weight / 0.4536
    pounds = round(pounds, 2)
    print(f"{weight} kg = {pounds} lb")
else: 
    print("Entered unit is invalid")