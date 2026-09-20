taxrate = 0.10
price = 25
inventorylimit = 500

def get_valid_input():
    value = input("Please enter a stock quantity, or enter 'quit' to exit: ")
    if value == "quit":
        return "quit"
    
    try:
        num = int(value)
    except ValueError:
        print("Please enter an integer value.")
        return None

    if num < 0:
        print("Please enter a positive integer.")
        return None

    return num

def process_delivery(current_total, new_value):
    quantity = current_total + new_value
    cost = quantity*price
    return quantity, cost

def calculate_tax(amount):
    return amount*taxrate

def generate_report(total_units, failed_attempts, total_cost, tax):
    print(f"Total Units Processed: {total_units}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")
    print(f"Delivery Tax: ${tax}")
    print(totalcost)
    print(f"Total Cost of Delivery (after Tax): ${total_cost+tax}")
    return None

failure = 0
quantity = 0
totalcost = 0
tax = 0

while True:
    entry = get_valid_input()

    if entry == "quit":
        break
    elif entry == None:
        failure += 1
        continue
    quantity, totalcost = process_delivery(quantity, entry)
    if quantity > inventorylimit:
        print("Your total inventory has exceeded 500!")
        break
    tax = calculate_tax(totalcost)

generate_report(quantity, failure, totalcost, tax)

    


