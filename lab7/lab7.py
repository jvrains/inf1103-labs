import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path

INVENTORY_FILE = Path(__file__).parent / "inventory.json"
BACKUP_FILE = Path(__file__).parent / "inventory_backup.json"


# class definitions
class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass

class Product(ABC):

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
    
    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass

class PhysicalProduct(Product, CanBeShipped):
 
    BASE_SHIPPING_COST = 5.00
    COST_PER_KG = 2.00
 
    def __init__(self, pid: str, name: str, price: float, stock: int, weight: float):
        super().__init__(pid, name, price, stock)
        self.__weight = weight
 
    def display_information(self) -> None:
        super().display_information()
        print(f"Weight: {self.__weight} kg")
 
    def get_fulfilment_info(self) -> str:
        return "This product requires physical shipping."
 
    def calculate_shipping_cost(self) -> float:
        return self.BASE_SHIPPING_COST + self.COST_PER_KG * self.__weight
 
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self.__weight
        return data

class DigitalProduct(Product):
    """A product that is downloaded. Download size is in megabytes."""
 
    def __init__(self, pid: str, name: str, price: float, stock: int, download_size: float):
        super().__init__(pid, name, price, stock)
        self.__download_size = download_size
 
    def display_information(self) -> None:
        super().display_information()
        print(f"Download Size: {self.__download_size} MB")
 
    def get_fulfilment_info(self) -> str:
        return "This product is delivered digitally."
 
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self.__download_size
        return data

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

def create_product(item: dict) -> Product:
    pid = item["id"]
    name = item["name"]
    price = float(item["price"])
    stock = int(item["stock"])
 
    if item["type"] == "physical":
        return PhysicalProduct(pid, name, price, stock, float(item["weight"]))
    if item["type"] == "digital":
        return DigitalProduct(pid, name, price, stock, float(item["download_size"]))
    raise ValueError("Unknown product type")

def load_inventory() -> Inventory:
    inventory = Inventory()
 
    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
 
        for item in data:
            inventory.add_product(create_product(item))
 
        print("inventory.json found.\nInventory loaded successfully.\n")
    except FileNotFoundError:
        print("Inventory not found.\nCreating...\n")
        save_inventory(inventory)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        shutil.copy(INVENTORY_FILE, BACKUP_FILE)
        print("inventory.json is corrupt or uses an old format.")
        print("A copy was saved as inventory_backup.json.")
        print("Starting with an empty inventory.\n")
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

def get_product_type() -> str:
    while True:
        choice = input("Product Type (1 = Physical, 2 = Digital): ")
        if choice == "1":
            return "physical"
        if choice == "2":
            return "digital"
        print("Please enter 1 or 2.")

def add_product(inventory: Inventory) -> None:
    print("\nAdd New Product")
    product_type = get_product_type()
    product_id = input("Product ID: ")
    name = input("Product Name: ")
    price = get_float("Price: ")
    stock = get_int("Stock Quantity: ")
 
    if product_type == "physical":
        weight = get_float("Weight (kg): ")
        product = PhysicalProduct(product_id, name, price, stock, weight)
    else:
        download_size = get_float("Download Size (MB): ")
        product = DigitalProduct(product_id, name, price, stock, download_size)
 
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
    print(product.get_fulfilment_info())
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")
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