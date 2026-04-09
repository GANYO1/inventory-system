# models/product.py

# This file contains the Product class — the data model for a single inventory item
# A model represents a real world thing in code
# Every product in your inventory system is an instance of this class


class Product:
    # __init__ is the constructor — it runs automatically when you create a new Product
    # It sets up the initial state of the product with the values you pass in
    # self refers to the specific instance being created
    # Every product has its own id, name, price and quantity stored separately
    def __init__(self, id, name, price, quantity):
        # Store the product ID on this instance
        # Used to uniquely identify this product — no two products share an ID
        self.id = id

        # Store the product name on this instance
        # Example: "Laptop", "Mouse", "Keyboard"
        self.name = name

        # Store the price on this instance
        # Stored as a float to support decimal values like 499.99
        self.price = price

        # Store the quantity in stock on this instance
        # Represents how many units of this product are available
        self.quantity = quantity

    def update_quantity(self, new_quantity):
        # This method safely updates the quantity of this product
        # It validates the input before making any changes
        # This is encapsulation — the validation lives here, not scattered everywhere

        # isinstance checks if new_quantity is actually an integer
        # You cannot have 2.5 units of a product — quantity must be a whole number
        # If it's not an integer raise TypeError with a clear message
        if not isinstance(new_quantity, int):
            raise TypeError("Quantity must be a whole number")

        # Quantity cannot be negative — you cannot have -5 products in stock
        # If it's negative raise ValueError with a clear message
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")

        # Both checks passed — safe to update the quantity
        # self.quantity is updated on this specific product instance
        self.quantity = new_quantity

    def update_price(self, new_price):
        # This method safely updates the price of this product
        # It validates the input before making any changes

        # Price can be either int or float — both are valid number types
        # (int, float) is a tuple of acceptable types for isinstance to check against
        # If it's neither raise TypeError
        if not isinstance(new_price, (int, float)):
            raise TypeError("Price must be a number")

        # Price must be greater than zero — a product cannot be free or have negative price
        # <= 0 catches both zero and negative values
        if new_price <= 0:
            raise ValueError("Price must be greater than zero")

        # Both checks passed — safe to update the price
        self.price = new_price

    def is_low_stock(self, threshold=5):
        # Returns True if this product's quantity is below the threshold
        # Returns False if quantity is at or above the threshold
        # threshold=5 means if no threshold is passed, 5 is used by default
        # Example: if quantity is 2 and threshold is 5, returns True
        # This is used to filter low stock products across the inventory
        return self.quantity < threshold

    def stock_value(self):
        # Calculates the total monetary value of this product's stock
        # Multiplies price by quantity
        # Example: Laptop at GHS 499.99 with 30 units = GHS 14,999.70
        # Used when calculating total inventory value
        return self.price * self.quantity

    def to_dict(self):
        # Converts this Product instance into a plain Python dictionary
        # This is necessary because JSON cannot serialize a Python object directly
        # Before saving to a file or sending as an API response
        # the object must be converted to a dictionary first
        # Each key in the dictionary matches the attribute name on the object
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity
        }

    def __repr__(self):
        # Controls what appears when you print a Product instance
        # Without this Python would show something like <Product object at 0x000001>
        # which is meaningless to a human
        # With this it shows: Product(1001, Laptop, GHS 499.99, qty: 30)
        # __repr__ is a special Python method — the double underscores mean
        # Python calls it automatically when you print the object
        return f"Product({self.id}, {self.name}, GHS {self.price}, qty: {self.quantity})"




































































# class Product:
#     def __init__(self, id, name, price, quantity):
#         self.id = id
#         self.name = name
#         self.price = price
#         self.quantity = quantity

#     def update_quantity(self, new_quantity):
#         if not isinstance(new_quantity, int):
#             raise TypeError("Quantity must be a whole number")
#         if new_quantity < 0:
#             raise ValueError("Quantity cannot be negative")
#         self.quantity = new_quantity

#     def update_price(self, new_price):
#         if not isinstance(new_price, (int, float)):
#             raise TypeError("Price must be a number")
#         if new_price <= 0:
#             raise ValueError("Price must be greater than zero")
#         self.price = new_price

#     def is_low_stock(self, threshold=5):
#         return self.quantity < threshold

#     def stock_value(self):
#         return self.price * self.quantity

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "price": self.price,
#             "quantity": self.quantity
#         }

#     def __repr__(self):
#         return f"Product({self.id}, {self.name}, GHS {self.price}, qty: {self.quantity})"