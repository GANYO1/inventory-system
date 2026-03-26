import sqlite3


class Database:
    def __init__(self, db_path="data/inventory.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        return self

    def disconnect(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def create_suppliers_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT
            )
        """)
        return "Suppliers table ready"

    def create_products_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                supplier_id INTEGER,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """)
        return "Products table ready"

    def add_supplier(self, id, name, phone):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO suppliers (id, name, phone) VALUES (?, ?, ?)",
            (id, name, phone)
        )
        return f"Added supplier {name}"

    def add_product(self, id, name, price, quantity, supplier_id=None):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO products (id, name, price, quantity, supplier_id) VALUES (?, ?, ?, ?, ?)",
            (id, name, price, quantity, supplier_id)
        )
        return f"Added product {name}"

    def get_products_with_suppliers(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT products.name, suppliers.name
            FROM products
            LEFT JOIN suppliers ON products.supplier_id = suppliers.id
        """)
        return cursor.fetchall()

    def get_low_stock(self, threshold=5):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM products WHERE quantity < ?",
            (threshold,)
        )
        return cursor.fetchall()

    def get_total_value(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(price * quantity) FROM products")
        result = cursor.fetchone()[0]
        return result if result else 0.0
    
    def get_all_products(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        return [
            {"id": r[0], "name": r[1], "price": r[2], 
            "quantity": r[3], "supplier_id": r[4]}
            for r in rows
        ]

    def find_product(self, product_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {"id": row[0], "name": row[1], "price": row[2],
                "quantity": row[3], "supplier_id": row[4]}


if __name__ == "__main__":
    db = Database()
    db.connect()

    print(db.create_suppliers_table())
    print(db.create_products_table())

    print(db.add_supplier(1, "TechSource Ghana", "0244000001"))
    print(db.add_supplier(2, "Accra Electronics", "0244000002"))

    print(db.add_product(1001, "Laptop", 499.99, 30, supplier_id=1))
    print(db.add_product(1002, "Mouse", 29.99, 2, supplier_id=1))
    print(db.add_product(1003, "Keyboard", 49.99, 0, supplier_id=2))
    print(db.add_product(1004, "Monitor", 299.99, 8, supplier_id=2))
    print(db.add_product(1005, "Headphones", 89.99, 3))

    print("\nProducts with Supplier Names:")
    for row in db.get_products_with_suppliers():
        print(row)

    print("\nLow Stock Products:")
    for row in db.get_low_stock():
        print(row)

    print(f"\nTotal Inventory Value: GHS {db.get_total_value():,.2f}")

    db.disconnect()