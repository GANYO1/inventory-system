# services/inventory_manager.py

from models.product import Product
import json


class InventoryManager:
    def __init__(self, filename="data/inventory.json"):
        self.filename = filename
        self.inventory = []

    def add_product(self, id, name, price, quantity):
        for product in self.inventory:
            if product.id == id:
                raise ValueError(f"Product ID {id} already exists")
        new_product = Product(id, name, price, quantity)
        self.inventory.append(new_product)
        return f"Added {name} to inventory"

    def remove_product(self, product_id):
        for product in self.inventory:
            if product.id == product_id:
                product_name = product.name
                self.inventory.remove(product)
                return f"Removed {product_name} from inventory"
        raise ValueError(f"Product ID {product_id} not found")

    def find_product(self, product_id):
        for product in self.inventory:
            if product.id == product_id:
                return product
        return None

    def get_low_stock(self, threshold=5):
        low = []
        for product in self.inventory:
            if product.is_low_stock(threshold):
                low.append(product)
        return low

    def get_total_value(self):
        total = 0
        for product in self.inventory:
            total += product.stock_value()
        return total

    def save(self):
        try:
            with open(self.filename, "w") as file:
                json.dump([p.to_dict() for p in self.inventory], file, indent=4)
            return f"Inventory saved to {self.filename}"
        except Exception as e:
            return f"Failed to save inventory: {e}"

    def load(self):
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
            self.inventory = [
                Product(p["id"], p["name"], p["price"], p["quantity"])
                for p in data
            ]
            return f"Loaded {len(self.inventory)} products from {self.filename}"
        except FileNotFoundError:
            self.inventory = []
            return "No saved inventory found. Starting fresh."
        except json.JSONDecodeError:
            self.inventory = []
            return "Corrupted inventory file. Starting fresh."