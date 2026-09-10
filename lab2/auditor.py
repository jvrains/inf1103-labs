# lab 2
#1
i = 0
a=""
#2,3,4,5,6
while a != "quit":
    add = input("Please enter a stock quantity, or enter 'quit' to exit: ")
    if add=='quit':
        break
    elif add.lstrip('-').isdigit():
        num = int(add)
        if num < 0:\
            print("Please enter a positive integer.")
        else:
            i+=int(num)
    else:
        print("Please enter an integer value.")
        continue
        