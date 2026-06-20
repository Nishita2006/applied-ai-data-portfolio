#wrap everything within a while loop so tht they can go back and forth between adding and removing items
# let them add quantity of items as well
#calculate the total in the end


items = ["onions", "spinach", "cabbage", "carrots", "tomatoes", "potatoes"]
price = [2,4,6,2,4,3]
cart = []
print("Below are the available food items: ")
for x in range(len(items)):
    print(f"{items[x]} : ${price[x]}")


decision = ""

while decision !="q":
    decision = input("Would you like to add, remove or show items from your cart? (or q to quit) ")
    decision = decision.lower()

    if decision == "add":
        add = input("Enter the items you would like to add to your cart? (or q to exit):")
        if add not in items:
            print("We don't have the entered veggie")        
        else:
            quantity_add = int(input("How many would you like to add? "))
            for x in range(quantity_add):
                cart.append(add)

        
    elif decision == "remove":
        remove = input("Enter the items you would like to remove from your cart? (or q to exit):")
        
        if cart == []:
            print("Your cart is empty. Nothing can be removed")
        elif remove not in cart:
            print("You don't have the entered veggie in your cart")        
        else:
            quantity_remove = int(input("How many would you like to remove? "))
            for x in range(quantity_remove):
                cart.remove(remove)       

    elif decision == "show": 
        total_price = 0       
        for food in set(cart):
            cart_price = items.index(food)
            index = price[cart_price]
            print(f"{food} x{cart.count(food)} : ${index * quantity_add}")
            total_price += index

    else:
        print("Invalid option.")
    
    
    print(f"{food} x{cart.count(food)} : ${index * quantity_add}")

print(f"The total is ${total_price} ")



print("Thank you for shopping!!")

  