# lab 2
#1
i = 0
failure = 0
#2,3,4,5,6,8
while True:
    add = input("Please enter a stock quantity, or enter 'quit' to exit: ")
    if add=='quit':
        break
    elif add.lstrip('-').isdigit():
        num = int(add)
        if num < 0:
            failure+=1
            print("Please enter a positive integer.")
        else:
            i+=int(num)
    else:
        failure+=1
        print("Please enter an integer value.")
        continue

 #8
print(f"Total Units Processed: {i}") 
print(f"Number of Failed/Rejected Entries: {failure}")