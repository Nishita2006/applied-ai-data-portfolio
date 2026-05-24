#Pattern triangle
rows = int(input("Enter the number of rows:"))
symbol= input("Enter a symbol: ")

for x in range(rows + 1):
    for y in range(x):
        print(symbol, end = "")
    print()
print()

#Inverted pattern triangle
rows = int(input("Enter the number of rows:"))
symbol= input("Enter a symbol: ")

for x in range(rows + 1):
    for y in (range(rows, x , -1)):
        print(symbol, end = "")
    print()


