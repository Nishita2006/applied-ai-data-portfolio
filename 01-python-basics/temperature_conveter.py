# Temperature converter
unit = input("Enter a unit(Celsius or Fahrenheit):")
temperature = input("Enter a temperature:")
temperature = float(temperature)
unit = unit.lower()
if unit == "celsius":
    fahrenheit = temperature * (9/5) + 32 
    fahrenheit = round(fahrenheit,2)
    print(f"{temperature} celsius = {fahrenheit} fahrenheit")
elif unit == "fahrenheit":
    celsius = (temperature - 32) / (9/5)
    celsius = round(celsius, 2)
    print(f"{temperature} fahrenheit = {celsius} celsius")
else:
    print("Entered unit is invalid")