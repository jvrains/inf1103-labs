import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path

INVENTORY_FILE = Path(__file__).parent / "inventory.json"
BACKUP_FILE = Path(__file__).parent / "inventory_backup.json"


# ---------------------------------------------------------------------------
# Supplier (association with Product)
# ---------------------------------------------------------------------------
class Supplier:
    """Who supplies a product. Exists independently of any Product."""

    def __init__(self, supplier_id: str, name: str, contact_email: str):
        self.__supplier_id: str = supplier_id
        self.__name: str = name
        self.__contact_email: str = contact_email

    def get_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    def display_information(self) -> None:
        print(
            f"Supplier ID: {self.__supplier_id} | Name: {self.__name} | "
            f"Email: {self.__contact_email}"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.__supplier_id,
            "name": self.__name,
            "contact_email": self.__contact_email,
        }


# ---------------------------------------------------------------------------
# Product classes
# ---------------------------------------------------------------------------
class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


class Product(ABC):

    def __init__(self, pid: str, name: str, price: float, stock: int,
                 supplier: Supplier):
        self.__pid: str = pid
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        # Association: Product keeps a reference to a Supplier it does not own
        self.__supplier: Supplier = supplier

    def get_id(self) -> str:
        return self.__pid

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def update_stock(self, quantity: int) -> bool:
        """Parent contract: any quantity of 0 or more is accepted, negative is rejected.
        Both subclasses inherit this unchanged, so they preserve it (LSP)."""
        if quantity < 0:
            return False
        self.__stock = quantity
        return True

    def display_information(self) -> None:
        print(
            f"ID: {self.__pid} | Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | Stock: {self.__stock} | "
            f"Supplier: {self.__supplier.get_name()}"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.__pid,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
            "supplier": self.__supplier.to_dict(),
        }

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass


class PhysicalProduct(Product, CanBeShipped):

    BASE_SHIPPING_COST: float = 5.00
    COST_PER_KG: float = 2.00

    def __init__(self, pid: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float):
        super().__init__(pid, name, price, stock, supplier)
        self.__weight: float = weight

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

    def __init__(self, pid: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float):
        super().__init__(pid, name, price, stock, supplier)
        self.__download_size: float = download_size

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


# ---------------------------------------------------------------------------
# Inventory (aggregation of Product)
# ---------------------------------------------------------------------------
class Inventory:
    """Groups existing Product objects. It does not create or destroy them."""

    def __init__(self):
        self.__products: list[Product] = []

    def get_products(self) -> list[Product]:
        return list(self.__products)

    def add_product(self, product: Product) -> bool:
        if self.find_product(product.get_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def remove_product(self, product_id: str) -> Product | None:
        """Remove the reference and hand the Product back; it is not destroyed."""
        product = self.find_product(product_id)
        if product is not None:
            self.__products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:
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
        # Polymorphism: each object runs its own display_information()
        for product in self.__products:
            product.display_information()
            print(product.get_fulfilment_info())
            print()
        print("-------------------------\n")

    def to_list(self) -> list[dict]:
        return [product.to_dict() for product in self.__products]


# ---------------------------------------------------------------------------
# Order and OrderLine (composition)
# ---------------------------------------------------------------------------
class OrderLine:
    """One product and quantity inside an Order. Only Order creates these."""

    def __init__(self, product: Product, quantity: int):
        # Association: the line refers to a Product but does not own it
        self.product: Product = product
        self.quantity: int = quantity

    def calculate_subtotal(self) -> float:
        return self.product.get_price() * self.quantity

    def display_information(self) -> None:
        print(
            f"{self.product.get_name()} x {self.quantity} "
            f"@ ${self.product.get_price():.2f} = ${self.calculate_subtotal():.2f}"
        )


class Order:
    """Composition: Order creates, owns and removes its OrderLine objects."""

    def __init__(self, order_id: str):
        self.order_id: str = order_id
        self.__order_lines: list[OrderLine] = []

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)  # created inside the Order
        self.__order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        for line in self.__order_lines:
            if line.product.get_id() == product_id:
                self.__order_lines.remove(line)
                return True
        return False

    def get_line_count(self) -> int:
        return len(self.__order_lines)

    def calculate_total(self) -> float:
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def display_order(self) -> None:
        print(f"\nOrder {self.order_id}")
        print("-------------------------")
        for line in self.__order_lines:
            line.display_information()
        print(f"Total: ${self.calculate_total():.2f}")
        print("-------------------------\n")


# ---------------------------------------------------------------------------
# LSP / polymorphism helper
# ---------------------------------------------------------------------------
def show_product_details(product: Product) -> None:
    """Works with any Product subclass without checking which one it is."""
    product.display_information()
    print(product.get_fulfilment_info())


# ---------------------------------------------------------------------------
# File handling
# ---------------------------------------------------------------------------
DEFAULT_SUPPLIER_ID = "S000"


def get_or_create_supplier(data: dict | None, suppliers: dict[str, Supplier]) -> Supplier:
    """Reuse one Supplier object per supplier ID so products share it."""
    if data is None:
        data = {"id": DEFAULT_SUPPLIER_ID, "name": "Unknown Supplier",
                "contact_email": "-"}
    supplier_id = data["id"]
    if supplier_id not in suppliers:
        suppliers[supplier_id] = Supplier(supplier_id, data["name"], data["contact_email"])
    return suppliers[supplier_id]


def create_product(item: dict, suppliers: dict[str, Supplier]) -> Product:
    pid = item["id"]
    name = item["name"]
    price = float(item["price"])
    stock = int(item["stock"])
    supplier = get_or_create_supplier(item.get("supplier"), suppliers)

    if item["type"] == "physical":
        return PhysicalProduct(pid, name, price, stock, supplier, float(item["weight"]))
    if item["type"] == "digital":
        return DigitalProduct(pid, name, price, stock, supplier, float(item["download_size"]))
    raise ValueError("Unknown product type")


def load_inventory(suppliers: dict[str, Supplier]) -> Inventory:
    inventory = Inventory()

    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            inventory.add_product(create_product(item, suppliers))

        print("inventory.json found.\nInventory loaded successfully.\n")
    except FileNotFoundError:
        print("Inventory not found.\nCreating...\n")
        save_inventory(inventory)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        shutil.copy(INVENTORY_FILE, BACKUP_FILE)
        print("inventory.json is corrupt or uses an old format.")
        print("A copy was saved as inventory_backup.json.")
        print("Starting with an empty inventory.\n")
        suppliers.clear()
        inventory = Inventory()

    return inventory


def save_inventory(inventory: Inventory) -> None:
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory.to_list(), f, indent="\t")


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------
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


def get_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
        except ValueError:
            pass
        print("Please enter a whole number greater than 0.")


def menu() -> int:
    print("------ MENU ------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Remove Product")
    print("6. Create Order")
    print("7. Save Inventory")
    print("8. Exit")
    print("------------------\n")

    while True:
        try:
            option = int(input("Enter option: "))
            if option in range(1, 9):
                return option
        except ValueError:
            pass
        print("Please input an option between 1-8.")


def get_product_type() -> str:
    while True:
        choice = input("Product Type (1 = Physical, 2 = Digital): ")
        if choice == "1":
            return "physical"
        if choice == "2":
            return "digital"
        print("Please enter 1 or 2.")


def choose_supplier(suppliers: dict[str, Supplier]) -> Supplier:
    """Pick an existing supplier by ID, or create a new one."""
    if suppliers:
        print("Existing suppliers:")
        for supplier in suppliers.values():
            supplier.display_information()

    supplier_id = input("Supplier ID: ")
    if supplier_id in suppliers:
        return suppliers[supplier_id]

    print("New supplier.")
    name = input("Supplier Name: ")
    email = input("Supplier Email: ")
    supplier = Supplier(supplier_id, name, email)
    suppliers[supplier_id] = supplier
    return supplier


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def add_product(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nAdd New Product")
    product_type = get_product_type()
    product_id = input("Product ID: ")
    name = input("Product Name: ")
    price = get_float("Price: ")
    stock = get_int("Stock Quantity: ")
    supplier = choose_supplier(suppliers)

    product: Product
    if product_type == "physical":
        weight = get_float("Weight (kg): ")
        product = PhysicalProduct(product_id, name, price, stock, supplier, weight)
    else:
        download_size = get_float("Download Size (MB): ")
        product = DigitalProduct(product_id, name, price, stock, supplier, download_size)

    if inventory.add_product(product):
        print("\nProduct added successfully!\n")
    else:
        print("\nA product with this ID already exists.\n")


def update_stock(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ")
    product = inventory.find_product(product_id)

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
    product = inventory.find_product(product_id)

    if product is None:
        print("No product with this ID was found.\n")
        return

    print("\nProduct Found")
    print("-------------------------")
    show_product_details(product)
    product.get_supplier().display_information()
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")
    print("-------------------------\n")


def remove_product(inventory: Inventory) -> None:
    print("\nRemove Product")
    product_id = input("Enter Product ID: ")
    product = inventory.remove_product(product_id)

    if product is None:
        print("No product with this ID was found.\n")
    else:
        print(f"{product.get_name()} was removed from the inventory.\n")


def create_order(inventory: Inventory, order_number: int) -> None:
    print("\nCreate Order")
    order = Order(f"O{order_number:03d}")

    while True:
        product_id = input("Product ID (leave blank to finish): ")
        if product_id == "":
            break
        product = inventory.find_product(product_id)
        if product is None:
            print("No product with this ID was found.")
            continue
        quantity = get_positive_int("Quantity: ")
        order.add_order_line(product, quantity)
        print(f"Added {quantity} x {product.get_name()}")

    if order.get_line_count() == 0:
        print("Order cancelled: no items added.\n")
        return

    order.display_order()


def main() -> None:
    print("=========================================")
    print("       INVENTORY MANAGEMENT SYSTEM       ")
    print("=========================================\n")

    suppliers: dict[str, Supplier] = {}
    inventory = load_inventory(suppliers)
    order_number = 1

    while True:
        option = menu()

        if option == 1:
            inventory.display_all()
        elif option == 2:
            add_product(inventory, suppliers)
        elif option == 3:
            update_stock(inventory)
        elif option == 4:
            search_product(inventory)
        elif option == 5:
            remove_product(inventory)
        elif option == 6:
            create_order(inventory, order_number)
            order_number += 1
        elif option == 7:
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
