# lab 2
#1
i = 0
failure = 0
#2,3,4,5,6,7,8
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
            i+=num
    else:
        failure+=1
        print("Please enter an integer value.")
    if i > 500:
        print("Your total inventory has exceeded 500!")
        break

#8
print(f"Total Units Processed: {i}") 
print(f"Number of Failed/Rejected Entries: {failure}")

'''
self reflection task
hitting limitation that the container terminates after run is concluded, therefore output file stored locally 
within the container also vanishes

'''