import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

# Let the tests import lab9.py from the folder above
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lab9 import (  # noqa: E402
    BulkDiscount,
    DigitalProduct,
    DiscountStrategy,
    Inventory,
    NoDiscount,
    Order,
    PercentageDiscount,
    PhysicalProduct,
    Product,
    ProductFactory,
    StudentDiscount,
    Supplier,
    get_positive_float,
    load_products,
)

SUPPLIER = Supplier("S001", "Logitech", "sales@logitech.com")

CSV_TEXT = (
    "product_type,product_id,name,price,stock_quantity\n"
    "physical,P001,Desk Lamp,25.00,10\n"
    "digital,D001,Photo Editor,49.90,100\n"
    "service,S001,Installation,30.00,5\n"
    "physical,P002,Office Chair,abc,3\n"
    "physical,P003,Monitor Stand,39.50,7\n"
)


def order_totalling_250(discount: DiscountStrategy | None = None) -> Order:
    order = Order("O001", discount)
    chair = ProductFactory.create("physical", "P1", "Chair", 50.0, 10, SUPPLIER, weight=5.0)
    software = ProductFactory.create("digital", "D1", "Software", 100.0, 10, SUPPLIER)
    order.add_order_line(chair, 3)     # 150
    order.add_order_line(software, 1)  # 100
    return order


class TestStrategy(unittest.TestCase):

    def test_default_is_no_discount(self):
        order = order_totalling_250()
        self.assertIsInstance(order.discount, NoDiscount)
        self.assertAlmostEqual(order.calculate_total(), 250.0)

    def test_bulk_discount(self):
        self.assertAlmostEqual(order_totalling_250(BulkDiscount(200, 20)).calculate_total(), 230.0)

    def test_bulk_discount_below_threshold(self):
        self.assertAlmostEqual(BulkDiscount(200, 20).apply(199.0), 199.0)

    def test_set_discount_changes_strategy(self):
        order = order_totalling_250(BulkDiscount(200, 20))
        self.assertAlmostEqual(order.calculate_total(), 230.0)
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225.0)

    def test_student_discount(self):
        self.assertAlmostEqual(order_totalling_250(StudentDiscount()).calculate_total(), 237.5)

    def test_new_strategy_needs_no_change_to_order(self):
        class HalfPrice(DiscountStrategy):
            def apply(self, total: float) -> float:
                return total / 2

        self.assertAlmostEqual(order_totalling_250(HalfPrice()).calculate_total(), 125.0)

    def test_two_orders_can_share_one_strategy(self):
        shared = PercentageDiscount(10)
        a = order_totalling_250(shared)
        b = order_totalling_250(shared)
        self.assertIs(a.discount, b.discount)
        self.assertAlmostEqual(a.calculate_total(), 225.0)
        self.assertAlmostEqual(b.calculate_total(), 225.0)


class TestFactory(unittest.TestCase):

    def test_creates_physical(self):
        product = ProductFactory.create("physical", "P1", "Lamp", 25.0, 10, SUPPLIER, weight=1.5)
        self.assertIsInstance(product, PhysicalProduct)
        self.assertIsInstance(product, Product)

    def test_creates_digital(self):
        product = ProductFactory.create("digital", "D1", "Editor", 49.9, 100, SUPPLIER)
        self.assertIsInstance(product, DigitalProduct)

    def test_unknown_type_raises_clear_error(self):
        with self.assertRaises(ValueError) as context:
            ProductFactory.create("service", "S1", "Installation", 30.0, 5, SUPPLIER)
        self.assertEqual(str(context.exception), "Unknown product type: service")


class TestValidation(unittest.TestCase):

    def test_price_must_be_greater_than_zero(self):
        for bad_price in (0, -5):
            with self.assertRaises(ValueError):
                ProductFactory.create("physical", "P1", "Lamp", bad_price, 10, SUPPLIER)

    def test_stock_cannot_be_negative(self):
        with self.assertRaises(ValueError):
            ProductFactory.create("digital", "D1", "Editor", 10.0, -1, SUPPLIER)

    def test_update_stock_rejects_negative_for_both_types(self):
        for product_type in ("physical", "digital"):
            product = ProductFactory.create(product_type, "X1", "Item", 10.0, 5, SUPPLIER)
            with self.assertRaises(ValueError):
                product.update_stock(-3)
            self.assertEqual(product.get_stock(), 5)

    def test_order_line_quantity_must_be_positive(self):
        product = ProductFactory.create("physical", "P1", "Lamp", 25.0, 10, SUPPLIER)
        order = Order("O001")
        for bad_quantity in (0, -2):
            with self.assertRaises(ValueError):
                order.add_order_line(product, bad_quantity)
        self.assertEqual(order.get_line_count(), 0)


class TestUserInput(unittest.TestCase):

    def test_get_positive_float_asks_again(self):
        output = io.StringIO()
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]), redirect_stdout(output):
            value = get_positive_float("Price: ")
        self.assertEqual(value, 12.50)
        self.assertEqual(output.getvalue().splitlines(), [
            "Please enter a valid number, e.g. 12.50",
            "Please enter a number greater than zero.",
        ])


class TestLoadProducts(unittest.TestCase):

    def test_bad_rows_skipped_and_valid_rows_load(self):
        inventory = Inventory()
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "products.csv"
            path.write_text(CSV_TEXT, encoding="utf-8")
            with redirect_stdout(output):
                load_products(str(path), inventory, SUPPLIER)

        text = output.getvalue()
        self.assertEqual(len(inventory.get_products()), 3)
        self.assertIsNone(inventory.find_product("S001"))
        self.assertIsNone(inventory.find_product("P002"))
        self.assertIn("Unknown product type: service", text)
        self.assertIn("could not convert string to float: 'abc'", text)
        self.assertTrue(text.strip().endswith("3 products loaded.\nLoad attempt finished."))

    def test_missing_file_is_handled(self):
        inventory = Inventory()
        output = io.StringIO()
        with redirect_stdout(output):
            load_products("missing_products.csv", inventory, SUPPLIER)

        self.assertEqual(output.getvalue().splitlines(), [
            "Products file not found: missing_products.csv",
            "Load attempt finished.",
        ])
        self.assertEqual(len(inventory.get_products()), 0)


if __name__ == "__main__":
    unittest.main()
