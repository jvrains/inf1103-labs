import json
from pathlib import Path


# class definitions

class Product:

    def __init__(self, pid: str, name: str, price: float, stock: int):
        self.__pid = pid
        self.__name = name
        self.__price = price
        self.__stock = stock
 
    def get_id(self) -> str:
        return self.__pid
 
    def get_name(self) -> str:
        return self.__name
 
    def get_stock(self) -> int:
        return self.__stock
 
    def update_stock(self, quantity: int) -> bool:
        if quantity < 0:
            return False
        self.__stock = quantity
        return True
 
    def display_information(self) -> None:
        print(
            f"ID: {self.__pid} | Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | Stock: {self.__stock}"
        )
 
    def to_dict(self) -> dict:
        return {
            "id": self.__pid,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
        }

class Inventory:

    def __init__(self):
        self.__products = []
 
    def add_product(self, product: Product) -> bool:
        if self.search_product(product.get_id()) is not None:
            return False
        self.__products.append(product)
        return True
 
    def search_product(self, product_id: str) -> Product | None:
        for product in self.__products:
            if product.get_id() == product_id:
                return product
        return None
 
    def display_all(self) -> None:
        if not self.__products:
            print("\nInventory is currently empty\n")
            return
 
        print("\nCurrent Inventory")
        print("-------------------------")
        for product in self.__products:
            product.display_information()
        print("-------------------------\n")
 
    def to_list(self) -> list[dict]:
        return [product.to_dict() for product in self.__products]
    
INVENTORY_FILE = Path(__file__).parent / "inventory.json"

# Checks for missing or corrupt files
def load_inventory() -> list[dict]:
    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:  
            a = json.load(f)
            print("inventory.json found.\n" \
            "Inventory loaded successfully.\n")
    except FileNotFoundError:
        with open(INVENTORY_FILE, "w", encoding="utf-8") as f:  
            a = []
            json.dump(a, f)
            print('Inventory not found.\n' \
            'Creating...\n')
    return a

def add_product(stock):
    product = {}
    print("\nAdd New Product")
    product['id'] = input("Product ID: ")
    product['name'] = input("Product Name: ")
    product['price'] = input("Price: ")
    product['stock'] = input("Stock Quantity: ")
    print("\nProduct added successfully!\n")
    stock.append(product)


def update_stock(stock):
    print("\nUpdate Stock")
    while True:
        get_id = input("Enter Product ID: ")
        for product in stock:
            if product['id'] == get_id:
                print("Product Found:")
                print(f"Name: {product['name']}")
                print(f"Current Stock: {product['stock']}")
                new = input("\nNew Stock Quantity: ")
                product['stock'] = new
                print("\nStock updated successfully!\n")
                return
        print("Please enter a valid PID")
    
    
def search_product(stock):
    print("\nSearch Product")
    pid = input("Enter Product ID: ")
    for order in stock:
        if order['id'] == pid:
            print("\nProduct Found")
            print("-------------------------")
            print(f"ID: {order['id']}")
            print(f"Name: {order['name']}")
            print(f"Price: {order['price']}")
            print(f"Stock: {order['stock']}")
            print("-------------------------\n")
            return
    print("No product with this ID was found.\n")
    


def display_all(stock):
    if stock:
        print("\nCurrent Inventory")
        print("-------------------------")
        for entry in stock:
            print(f"ID: {entry['id']} | Name: {entry['name']} | Price: ${entry['price']} | Stock: {entry['stock']} ")
        print("-------------------------\n")
    else:
        print("\nInventory is currently empty\n")


def save_inventory(stock):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(stock, f, indent = "\t")
        return stock

def menu():
    print("------ MENU ------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("------------------\n")
    while True:
        try:
            option = int(input("Enter option: "))
            if option not in range(1,7):
                raise TypeError
            return option
        except TypeError:
            print("Please input an option between 1-6.")


def main():
    print("=========================================")
    print("       INVENTORY MANAGEMENT SYSTEM       ")
    print("=========================================\n")
    stock = load_inventory()
    while True:
        option = menu()
        if option == 1:
            display_all(stock)
            continue
        elif option == 2:
            add_product(stock)
        elif option == 3:
            update_stock(stock)
        elif option == 4:
            search_product(stock)
        elif option == 5:
            save_inventory(stock)
            print("\nSaving Inventory...")
            print("Inventory saved successfully to inventory.json.\n")
        else:
            save_inventory(stock)
            print("\nSaving inventory before exit...")
            print("Inventory saved successfully.\n")
            print("Thank you for using Inventory Management System.")
            print("Program Terminated.")
            break

main()