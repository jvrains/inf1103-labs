import csv
import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path

INVENTORY_FILE = Path(__file__).parent / "inventory.json"
BACKUP_FILE = Path(__file__).parent / "inventory_backup.json"
PRODUCTS_CSV = Path(__file__).parent / "products.csv"


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
        # Validation: Product owns its price and stock rules
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        if stock < 0:
            raise ValueError("Stock quantity cannot be negative.")
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

    def update_stock(self, quantity: int) -> None:
        """Parent contract: any quantity of 0 or more is accepted, negative raises
        ValueError. Both subclasses inherit this unchanged, so they preserve it (LSP)."""
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")
        self.__stock = quantity

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
        if weight < 0:
            raise ValueError("Weight cannot be negative.")
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
        if download_size < 0:
            raise ValueError("Download size cannot be negative.")
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
# Factory pattern: the one place that decides which Product class to build
# ---------------------------------------------------------------------------
class ProductFactory:
    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock_quantity: int, supplier: Supplier, weight: float = 0.0,
               download_size: float = 0.0) -> Product:
        if product_type == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity, supplier, weight)
        elif product_type == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity, supplier, download_size)
        else:
            raise ValueError(f"Unknown product type: {product_type}")


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
# Strategy pattern: interchangeable discounts
# ---------------------------------------------------------------------------
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        pass


class NoDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100.")
        self.__percentage: float = percentage

    def apply(self, total: float) -> float:
        return total * (1 - self.__percentage / 100)


class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, amount: float):
        if threshold < 0 or amount < 0:
            raise ValueError("Threshold and amount cannot be negative.")
        self.__threshold: float = threshold
        self.__amount: float = amount

    def apply(self, total: float) -> float:
        if total >= self.__threshold:
            return total - self.__amount
        return total


class StudentDiscount(DiscountStrategy):
    """Fourth strategy (Section 2.4): 5% off. Added without changing Order."""

    RATE: float = 0.05

    def apply(self, total: float) -> float:
        return total * (1 - self.RATE)


# ---------------------------------------------------------------------------
# Order and OrderLine (composition)
# ---------------------------------------------------------------------------
class OrderLine:
    """One product and quantity inside an Order. Only Order creates these."""

    def __init__(self, product: Product, quantity: int):
        # Validation: OrderLine protects its own quantity
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
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

    def __init__(self, order_id: str, discount: DiscountStrategy | None = None):
        self.order_id: str = order_id
        self.__order_lines: list[OrderLine] = []
        # Association: Order uses a strategy but does not own it (it can be shared)
        self.discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def set_discount(self, discount: DiscountStrategy) -> None:
        self.discount = discount

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

    def calculate_subtotal(self) -> float:
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def calculate_total(self) -> float:
        # No if/elif about discount types: the strategy decides
        return self.discount.apply(self.calculate_subtotal())

    def display_order(self) -> None:
        print(f"\nOrder {self.order_id}")
        print("-------------------------")
        for line in self.__order_lines:
            line.display_information()
        print(f"Subtotal: ${self.calculate_subtotal():.2f}")
        print(f"Total after discount: ${self.calculate_total():.2f}")
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
    """Build a product from a JSON dict, using the factory."""
    return ProductFactory.create(
        item["type"],
        item["id"],
        item["name"],
        float(item["price"]),
        int(item["stock"]),
        get_or_create_supplier(item.get("supplier"), suppliers),
        weight=float(item.get("weight", 0.0)),
        download_size=float(item.get("download_size", 0.0)),
    )


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


def save_inventory(inventory: Inventory) -> bool:
    try:
        with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(inventory.to_list(), f, indent="\t")
    except OSError:
        print("Could not save inventory.json.")
        return False
    return True


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    """Load products from a CSV file. Bad rows are reported and skipped."""
    try:
        file = open(path, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        loaded = 0
        with file:
            reader = csv.reader(file)
            next(reader, None)  # skip the header row
            for row in reader:
                try:
                    product_type, product_id, name, price, stock = row
                    product = ProductFactory.create(
                        product_type, product_id, name, float(price), int(stock), supplier
                    )
                except ValueError as error:
                    print(f"Skipped row {row}: {error}")
                    continue

                if inventory.add_product(product):
                    loaded += 1
                else:
                    print(f"Skipped row {row}: ID {product_id} already exists.")
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")


# ---------------------------------------------------------------------------
# Input helpers (exception handling: keep asking until the input is valid)
# ---------------------------------------------------------------------------
def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


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
    print("7. Load Products from CSV")
    print("8. Save Inventory")
    print("9. Exit")
    print("------------------\n")

    while True:
        try:
            option = int(input("Enter option: "))
            if option in range(1, 10):
                return option
        except ValueError:
            pass
        print("Please input an option between 1-9.")


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


def choose_discount() -> DiscountStrategy:
    print("Discount options:")
    print("1. No discount")
    print("2. 10% off")
    print("3. $20 off orders of $200 or more")
    print("4. Student discount (5% off)")
    # A dictionary maps each choice to a strategy, so no if/elif chain is needed
    options: dict[str, DiscountStrategy] = {
        "1": NoDiscount(),
        "2": PercentageDiscount(10),
        "3": BulkDiscount(200, 20),
        "4": StudentDiscount(),
    }
    while True:
        choice = input("Choose discount: ")
        if choice in options:
            return options[choice]
        print("Please enter 1, 2, 3 or 4.")


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def add_product(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nAdd New Product")
    product_type = get_product_type()
    product_id = input("Product ID: ")
    name = input("Product Name: ")
    price = get_positive_float("Price: ")
    stock = get_int("Stock Quantity: ")
    supplier = choose_supplier(suppliers)

    weight = 0.0
    download_size = 0.0
    if product_type == "physical":
        weight = get_float("Weight (kg): ")
    else:
        download_size = get_float("Download Size (MB): ")

    product = ProductFactory.create(product_type, product_id, name, price, stock,
                                    supplier, weight=weight, download_size=download_size)

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
    try:
        product.update_stock(new_stock)
    except ValueError as error:
        print(f"\nStock could not be updated: {error}\n")
    else:
        print("\nStock updated successfully!\n")


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

    order.set_discount(choose_discount())
    order.display_order()


def load_products_menu(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nLoad Products from CSV")
    print("Choose the supplier for these products.")
    supplier = choose_supplier(suppliers)
    print()
    load_products(str(PRODUCTS_CSV), inventory, supplier)
    print()


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
            load_products_menu(inventory, suppliers)
        elif option == 8:
            print("\nSaving Inventory...")
            if save_inventory(inventory):
                print("Inventory saved successfully to inventory.json.\n")
        else:
            print("\nSaving inventory before exit...")
            if save_inventory(inventory):
                print("Inventory saved successfully.\n")
            print("Thank you for using Inventory Management System.")
            print("Program Terminated.")
            break


if __name__ == "__main__":
    main()
