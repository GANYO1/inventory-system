# This file contains the InventoryManager class — the service layer of your system
# A service handles business logic — the operations you can perform on your data
# It sits between your API endpoints and your data models
# Think of it this way:
# Product (model)          — what a product IS
# InventoryManager (service) — what you can DO with products


# Import the Product class from the models folder
# InventoryManager works with Product instances — it needs to know what a Product is
from models.product import Product

# Import json to handle saving and loading inventory data to and from a file
import json


class InventoryManager:

    def __init__(self, filename="data/inventory.json"):
        # Constructor — runs when you create a new InventoryManager instance
        # filename is where inventory data will be saved and loaded from
        # default is "data/inventory.json" if no filename is provided

        # Store the filename on this instance so all methods can access it
        self.filename = filename

        # Start with an empty list — no products loaded yet
        # As products are added or loaded they go into this list
        # Each item in this list is a Product instance
        self.inventory = []

    def add_product(self, id, name, price, quantity):
        # Adds a new product to the inventory
        # First checks if a product with the same ID already exists
        # This prevents duplicate products which would cause data corruption

        # Loop through every existing product in the inventory list
        for product in self.inventory:
            # Check if any existing product has the same ID as the one being added
            if product.id == id:
                # Duplicate ID found — raise ValueError with a clear message
                # The caller is responsible for handling this error
                raise ValueError(f"Product ID {id} already exists")

        # No duplicate found — safe to create the new product
        # Creates a Product instance using the values passed in
        new_product = Product(id, name, price, quantity)

        # Add the new Product instance to the inventory list
        self.inventory.append(new_product)

        return f"Added {name} to inventory"

    def remove_product(self, product_id):
        # Finds and removes a product from the inventory by its ID
        # Loops through the inventory looking for a matching product

        for product in self.inventory:
            # Check if this product's ID matches the one we want to remove
            if product.id == product_id:
                # Save the name before removing — needed for the return message
                product_name = product.name

                # Remove this product from the inventory list
                # self.inventory.remove() finds and deletes the first matching item
                self.inventory.remove(product)

                # Return immediately after removing — no need to check remaining products
                # The return is INSIDE the if block so it only runs when product is found
                return f"Removed {product_name} from inventory"

        # Loop completed without finding the product
        # This line only runs if no product matched — raise ValueError
        raise ValueError(f"Product ID {product_id} not found")

    def find_product(self, product_id):
        # Searches the inventory for a product with the given ID
        # Returns the Product instance if found, None if not found

        for product in self.inventory:
            # Check if this product's ID matches what we're looking for
            if product.id == product_id:
                # Found it — return the actual Product instance
                # The caller gets a reference to the same object in memory
                # So any changes made to the returned product affect the inventory too
                return product

        # Loop completed without finding the product — return None
        # The caller must check for None before using the result
        return None

    def get_low_stock(self, threshold=5):
        # Returns a list of all products where quantity is below the threshold
        # threshold=5 means products with less than 5 units are considered low stock
        # If no threshold is passed, 5 is used by default

        # Start with an empty list to collect low stock products
        low = []

        for product in self.inventory:
            # Call is_low_stock on each Product instance
            # is_low_stock is defined in the Product class — it returns True or False
            # This is why we keep logic in the model — we reuse it here
            if product.is_low_stock(threshold):
                # This product is low on stock — add it to the list
                low.append(product)

        # Return the complete list of low stock products
        # If no products are low on stock this returns an empty list
        return low

    def get_total_value(self):
        # Calculates the total monetary value of all stock combined
        # Adds up price * quantity for every product in the inventory

        # Start at zero — will accumulate the total
        total = 0

        for product in self.inventory:
            # Call stock_value on each Product instance
            # stock_value is defined in the Product class — it returns price * quantity
            # += adds the result to the running total
            total += product.stock_value()

        # Return the final total after all products have been counted
        return total

    def save(self):
        # Saves the current inventory to a JSON file on disk
        # This makes the data persist after the program closes

        try:
            # Open the file in write mode — "w" creates the file if it doesn't exist
            # and overwrites it if it does
            # The "with" statement automatically closes the file when done
            # even if an error occurs
            with open(self.filename, "w") as file:
                # json.dump writes Python data to the file as JSON
                # [p.to_dict() for p in self.inventory] converts each Product instance
                # to a plain dictionary — JSON cannot serialize Python objects directly
                # indent=4 makes the JSON human readable with proper indentation
                json.dump([p.to_dict() for p in self.inventory], file, indent=4)

            return f"Inventory saved to {self.filename}"

        except Exception as e:
            # Something went wrong saving the file — disk full, permissions, etc
            # Return the error message instead of crashing
            return f"Failed to save inventory: {e}"

    def load(self):
        # Loads inventory data from the JSON file back into memory
        # Converts the raw dictionary data back into Product instances

        try:
            # Open the file in read mode — "r" reads an existing file
            with open(self.filename, "r") as file:
                # json.load reads the JSON from the file and converts it
                # back into Python data — a list of dictionaries
                data = json.load(file)

            # Convert each dictionary back into a Product instance
            # This is the reverse of to_dict() in the Product class
            # data is a list of dicts like [{"id": 1001, "name": "Laptop", ...}]
            # for each dict p we create Product(p["id"], p["name"], p["price"], p["quantity"])
            self.inventory = [
                Product(p["id"], p["name"], p["price"], p["quantity"])
                for p in data
            ]

            # Return how many products were loaded
            # len(self.inventory) counts the items in the list
            return f"Loaded {len(self.inventory)} products from {self.filename}"

        except FileNotFoundError:
            # The file doesn't exist yet — this is normal on first run
            # Start with an empty inventory instead of crashing
            self.inventory = []
            return "No saved inventory found. Starting fresh."

        except json.JSONDecodeError:
            # The file exists but contains invalid JSON — it may be corrupted
            # Start fresh instead of crashing
            self.inventory = []
            return "Corrupted inventory file. Starting fresh."



# from models.product import Product
# import json


# class InventoryManager:
#     def __init__(self, filename="data/inventory.json"):
#         self.filename = filename
#         self.inventory = []

#     def add_product(self, id, name, price, quantity):
#         for product in self.inventory:
#             if product.id == id:
#                 raise ValueError(f"Product ID {id} already exists")
#         new_product = Product(id, name, price, quantity)
#         self.inventory.append(new_product)
#         return f"Added {name} to inventory"

#     def remove_product(self, product_id):
#         for product in self.inventory:
#             if product.id == product_id:
#                 product_name = product.name
#                 self.inventory.remove(product)
#                 return f"Removed {product_name} from inventory"
#         raise ValueError(f"Product ID {product_id} not found")

#     def find_product(self, product_id):
#         for product in self.inventory:
#             if product.id == product_id:
#                 return product
#         return None

#     def get_low_stock(self, threshold=5):
#         low = []
#         for product in self.inventory:
#             if product.is_low_stock(threshold):
#                 low.append(product)
#         return low

#     def get_total_value(self):
#         total = 0
#         for product in self.inventory:
#             total += product.stock_value()
#         return total

#     def save(self):
#         try:
#             with open(self.filename, "w") as file:
#                 json.dump([p.to_dict() for p in self.inventory], file, indent=4)
#             return f"Inventory saved to {self.filename}"
#         except Exception as e:
#             return f"Failed to save inventory: {e}"

#     def load(self):
#         try:
#             with open(self.filename, "r") as file:
#                 data = json.load(file)
#             self.inventory = [
#                 Product(p["id"], p["name"], p["price"], p["quantity"])
#                 for p in data
#             ]
#             return f"Loaded {len(self.inventory)} products from {self.filename}"
#         except FileNotFoundError:
#             self.inventory = []
#             return "No saved inventory found. Starting fresh."
#         except json.JSONDecodeError:
#             self.inventory = []
#             return "Corrupted inventory file. Starting fresh."