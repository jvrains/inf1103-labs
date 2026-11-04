import json
from pathlib import Path

INVENTORY_FILE = Path(__file__).parent / "inventory.json"


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

def load_inventory() -> Inventory:
    inventory = Inventory()
 
    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
 
        for item in data:
            product = Product(
                item["id"],
                item["name"],
                float(item["price"]),
                int(item["stock"]),
            )
            inventory.add_product(product)
 
        print("inventory.json found.\nInventory loaded successfully.\n")
    except FileNotFoundError:
        print("Inventory not found.\nCreating...\n")
        save_inventory(inventory)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        print("inventory.json is corrupt.\nStarting with an empty inventory.\n")
        inventory = Inventory()
 
    return inventory
 
def save_inventory(inventory: Inventory) -> None:
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory.to_list(), f, indent="\t")

def get_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value >= 0:
                return value
        except ValueError:
            pass
        print("Please enter a number that is 0 or more.")
 
 
def get_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value >= 0:
                return value
        except ValueError:
            pass
        print("Please enter a whole number that is 0 or more.")
 
 
def menu() -> int:
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
            if option in range(1, 7):
                return option
        except ValueError:
            pass
        print("Please input an option between 1-6.")
 
def add_product(inventory: Inventory) -> None:
    print("\nAdd New Product")
    product_id = input("Product ID: ")
    name = input("Product Name: ")
    price = get_float("Price: ")
    stock = get_int("Stock Quantity: ")
 
    product = Product(product_id, name, price, stock)
    if inventory.add_product(product):
        print("\nProduct added successfully!\n")
    else:
        print("\nA product with this ID already exists.\n")
 
 
def update_stock(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ")
    product = inventory.search_product(product_id)
 
    if product is None:
        print("No product with this ID was found.\n")
        return
 
    print("Product Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}")
 
    new_stock = get_int("\nNew Stock Quantity: ")
    if product.update_stock(new_stock):
        print("\nStock updated successfully!\n")
    else:
        print("\nStock could not be updated.\n")
 
 
def search_product(inventory: Inventory) -> None:
    print("\nSearch Product")
    product_id = input("Enter Product ID: ")
    product = inventory.search_product(product_id)
 
    if product is None:
        print("No product with this ID was found.\n")
        return
 
    print("\nProduct Found")
    print("-------------------------")
    product.display_information()
    print("-------------------------\n")
 
def main() -> None:
    print("=========================================")
    print("       INVENTORY MANAGEMENT SYSTEM       ")
    print("=========================================\n")
 
    inventory = load_inventory()
 
    while True:
        option = menu()
 
        if option == 1:
            inventory.display_all()
        elif option == 2:
            add_product(inventory)
        elif option == 3:
            update_stock(inventory)
        elif option == 4:
            search_product(inventory)
        elif option == 5:
            print("\nSaving Inventory...")
            save_inventory(inventory)
            print("Inventory saved successfully to inventory.json.\n")
        else:
            print("\nSaving inventory before exit...")
            save_inventory(inventory)
            print("Inventory saved successfully.\n")
            print("Thank you for using Inventory Management System.")
            print("Program Terminated.")
            break
 
 
if __name__ == "__main__":
    main()