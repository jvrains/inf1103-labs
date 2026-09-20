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

    if num <= 0:
        print("Please enter a positive integer.")
        return None

    return num

def process_delivery(current_total, new_value):
    return current_total + new_value

def calculate_tax(amount):
    return amount*taxrate

def generate_report(total_units, failed_attempts, delivery):
    print(f"Total Units Processed: {total_units}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")
    print(f"Number of Deliveries: {delivery}")
    return None

failure = 0
totalcount = 0
deliveries = 0

while True:
    entry = get_valid_input()

    if entry == "quit":
        break
    elif entry == None:
        failure += 1
        continue
    totalcount = process_delivery(totalcount, entry)
    totalcost = entry*price
    deliveries += 1
    tax = calculate_tax(totalcost)
    if totalcount > inventorylimit:
        print("Your total inventory has exceeded 500!")
        break
    print(f"Delivery Tax: ${tax:.2f}")
    print(f"Total Cost of Delivery (after Tax): ${totalcost+tax:.2f}")
    
generate_report(totalcount, failure, deliveries)