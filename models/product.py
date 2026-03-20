# models/product.py


class Product:
    def __init__(self, id, name, price, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_quantity(self, new_quantity):
        if not isinstance(new_quantity, int):
            raise TypeError("Quantity must be a whole number")
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        self.quantity = new_quantity

    def update_price(self, new_price):
        if not isinstance(new_price, (int, float)):
            raise TypeError("Price must be a number")
        if new_price <= 0:
            raise ValueError("Price must be greater than zero")
        self.price = new_price

    def is_low_stock(self, threshold=5):
        return self.quantity < threshold

    def stock_value(self):
        return self.price * self.quantity

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity
        }

    def __repr__(self):
        return f"Product({self.id}, {self.name}, GHS {self.price}, qty: {self.quantity})"