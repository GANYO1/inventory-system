# This is the SQLite version of the database layer — used during development and learning
# SQLite stores data in a local file instead of a remote server
# It requires zero installation — built directly into Python
# This file was replaced by database_pg.py when we switched to PostgreSQL for production
# The SQL logic is identical — only the connection method and placeholder syntax differ
# SQLite uses ? as placeholders, PostgreSQL uses %s

# sqlite3 is Python's built-in SQLite library — no installation needed
import sqlite3


class Database:

    def __init__(self, db_path="data/inventory.db"):
        # Constructor — runs when you create a new Database instance
        # db_path is the file path where SQLite will store the database
        # Default is "data/inventory.db" if no path is provided
        # Unlike PostgreSQL, SQLite creates this file automatically if it doesn't exist
        self.db_path = db_path

        # conn stores the database connection
        # Set to None initially — connect() must be called before any operations
        self.conn = None

    def connect(self):
        # Opens a connection to the SQLite database file
        # If the file doesn't exist SQLite creates it automatically
        # This is different from PostgreSQL which requires a running server
        self.conn = sqlite3.connect(self.db_path)

        # Return self so connect() can be chained if needed
        return self

    def disconnect(self):
        # Safely closes the database connection
        # The "if self.conn" check prevents errors if called with no active connection
        if self.conn:
            # Commit any pending changes before closing
            # Ensures no data is lost if commit wasn't called explicitly
            self.conn.commit()

            # Close the connection to the SQLite file
            self.conn.close()

            # Set conn back to None to signal no active connection
            self.conn = None

    def create_suppliers_table(self):
        # Creates the suppliers table if it doesn't already exist
        # IF NOT EXISTS makes this safe to call multiple times
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,  -- unique identifier, no duplicates allowed
                name TEXT NOT NULL,      -- supplier name is required
                phone TEXT               -- phone is optional, can be NULL
            )
        """)
        # Note: no explicit commit here — disconnect() handles the final commit
        # In SQLite, DDL statements like CREATE TABLE are auto-committed in some modes
        return "Suppliers table ready"

    def create_products_table(self):
        # Creates the products table if it doesn't already exist
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,              -- unique product identifier
                name TEXT NOT NULL,                  -- product name is required
                price REAL NOT NULL,                 -- REAL allows decimal values like 499.99
                quantity INTEGER NOT NULL DEFAULT 0, -- defaults to 0 if not provided
                supplier_id INTEGER,                 -- optional link to a supplier
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                -- FOREIGN KEY enforces that supplier_id must exist in suppliers table
                -- Prevents linking a product to a supplier that doesn't exist
            )
        """)
        return "Products table ready"

    def add_supplier(self, id, name, phone):
        # Inserts a new supplier into the suppliers table
        cursor = self.conn.cursor()

        cursor.execute(
            # ? are placeholders — never put variables directly in SQL strings
            # This prevents SQL injection — malicious input that could destroy your database
            "INSERT INTO suppliers (id, name, phone) VALUES (?, ?, ?)",

            # Actual values passed as a tuple — SQLite safely substitutes them for ?
            (id, name, phone)
        )
        return f"Added supplier {name}"

    def add_product(self, id, name, price, quantity, supplier_id=None):
        # Inserts a new product into the products table
        # supplier_id=None means it's optional — a product can exist without a supplier
        # None is stored as NULL in the database
        cursor = self.conn.cursor()

        cursor.execute(
            # Five ? placeholders matching the five values being inserted
            "INSERT INTO products (id, name, price, quantity, supplier_id) VALUES (?, ?, ?, ?, ?)",
            (id, name, price, quantity, supplier_id)
        )
        return f"Added product {name}"

    def get_products_with_suppliers(self):
        # Returns each product paired with its supplier name
        # Uses a JOIN to pull data from two tables in a single query
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT products.name, suppliers.name
            FROM products
            -- LEFT JOIN includes ALL products even those without a supplier
            -- Products with no supplier show NULL for the supplier name
            -- INNER JOIN would exclude products with no supplier — not what we want
            LEFT JOIN suppliers ON products.supplier_id = suppliers.id
        """)

        # fetchall() returns all matching rows as a list of tuples
        # Each tuple: (product_name, supplier_name)
        return cursor.fetchall()

    def get_low_stock(self, threshold=5):
        # Returns all products where quantity is below the threshold
        # threshold=5 is the default — less than 5 units means low stock
        cursor = self.conn.cursor()

        cursor.execute(
            # WHERE quantity < ? filters only rows below the threshold
            "SELECT * FROM products WHERE quantity < ?",
            # Single value still needs to be a tuple — the comma makes it a tuple
            (threshold,)
        )

        # Return all matching rows as a list of tuples
        return cursor.fetchall()

    def get_total_value(self):
        # Calculates total monetary value of all stock using SQL
        # SUM() is faster than fetching all rows and calculating in Python
        cursor = self.conn.cursor()

        # SUM(price * quantity) multiplies price by quantity for each row
        # then adds all results into a single number
        cursor.execute("SELECT SUM(price * quantity) FROM products")

        # fetchone() gets the single result row
        # [0] extracts the first (and only) value — the sum
        result = cursor.fetchone()[0]

        # If products table is empty SUM returns NULL which becomes None in Python
        # Return 0.0 instead of None to avoid formatting errors
        return result if result else 0.0

    def get_all_products(self):
        # Retrieves every product from the database
        # Returns a list of dictionaries — easier to work with than tuples
        cursor = self.conn.cursor()

        # SELECT * returns all columns for every row in the products table
        cursor.execute("SELECT * FROM products")

        # fetchall() retrieves all rows at once as a list of tuples
        rows = cursor.fetchall()

        # Convert each tuple into a readable dictionary
        # r[0] = id, r[1] = name, r[2] = price, r[3] = quantity, r[4] = supplier_id
        # Dictionaries are easier to read and return as JSON than raw tuples
        return [
            {"id": r[0], "name": r[1], "price": r[2],
            "quantity": r[3], "supplier_id": r[4]}
            for r in rows
        ]

    def find_product(self, product_id):
        # Finds a single product by its ID
        # Returns a dictionary if found, None if not found
        cursor = self.conn.cursor()

        cursor.execute(
            # WHERE id = ? filters to only the row with this specific ID
            "SELECT * FROM products WHERE id = ?",
            # Single value as a tuple — the comma is required
            (product_id,)
        )

        # fetchone() gets only the first matching row
        # Returns None if no row matched the WHERE condition
        row = cursor.fetchone()

        if row is None:
            # No product found with that ID
            # Return None — the caller decides what to do with this
            return None

        # Product found — convert tuple to dictionary and return
        return {"id": row[0], "name": row[1], "price": row[2],
                "quantity": row[3], "supplier_id": row[4]}


# This block only runs when you execute this file directly: py database_v2.py
# It does NOT run when another file imports from this file
# Used to test the database layer independently without starting the full API
if __name__ == "__main__":
    # Create a Database instance — conn is None at this point
    db = Database()

    # Open the connection to the SQLite file
    # Creates data/inventory.db if it doesn't exist
    db.connect()

    # Create both tables — safe to run even if they already exist
    print(db.create_suppliers_table())
    print(db.create_products_table())

    # Insert two suppliers into the suppliers table
    print(db.add_supplier(1, "TechSource Ghana", "0244000001"))
    print(db.add_supplier(2, "Accra Electronics", "0244000002"))

    # Insert five products — some linked to suppliers, one without
    # supplier_id=1 links to TechSource Ghana
    # supplier_id=2 links to Accra Electronics
    # No supplier_id means supplier_id defaults to None — stored as NULL
    print(db.add_product(1001, "Laptop", 499.99, 30, supplier_id=1))
    print(db.add_product(1002, "Mouse", 29.99, 2, supplier_id=1))
    print(db.add_product(1003, "Keyboard", 49.99, 0, supplier_id=2))
    print(db.add_product(1004, "Monitor", 299.99, 8, supplier_id=2))
    print(db.add_product(1005, "Headphones", 89.99, 3))

    # Print each product alongside its supplier name using the JOIN query
    print("\nProducts with Supplier Names:")
    for row in db.get_products_with_suppliers():
        print(row)

    # Print all products where quantity is below 5
    print("\nLow Stock Products:")
    for row in db.get_low_stock():
        print(row)

    # Print total inventory value formatted with commas and 2 decimal places
    print(f"\nTotal Inventory Value: GHS {db.get_total_value():,.2f}")

    # Close the connection — commit all pending changes and close the file
    db.disconnect()



#     import sqlite3


# class Database:
#     def __init__(self, db_path="data/inventory.db"):
#         self.db_path = db_path
#         self.conn = None

#     def connect(self):
#         self.conn = sqlite3.connect(self.db_path)
#         return self

#     def disconnect(self):
#         if self.conn:
#             self.conn.commit()
#             self.conn.close()
#             self.conn = None

#     def create_suppliers_table(self):
#         cursor = self.conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS suppliers (
#                 id INTEGER PRIMARY KEY,
#                 name TEXT NOT NULL,
#                 phone TEXT
#             )
#         """)
#         return "Suppliers table ready"

#     def create_products_table(self):
#         cursor = self.conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS products (
#                 id INTEGER PRIMARY KEY,
#                 name TEXT NOT NULL,
#                 price REAL NOT NULL,
#                 quantity INTEGER NOT NULL DEFAULT 0,
#                 supplier_id INTEGER,
#                 FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
#             )
#         """)
#         return "Products table ready"

#     def add_supplier(self, id, name, phone):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "INSERT INTO suppliers (id, name, phone) VALUES (?, ?, ?)",
#             (id, name, phone)
#         )
#         return f"Added supplier {name}"

#     def add_product(self, id, name, price, quantity, supplier_id=None):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "INSERT INTO products (id, name, price, quantity, supplier_id) VALUES (?, ?, ?, ?, ?)",
#             (id, name, price, quantity, supplier_id)
#         )
#         return f"Added product {name}"

#     def get_products_with_suppliers(self):
#         cursor = self.conn.cursor()
#         cursor.execute("""
#             SELECT products.name, suppliers.name
#             FROM products
#             LEFT JOIN suppliers ON products.supplier_id = suppliers.id
#         """)
#         return cursor.fetchall()

#     def get_low_stock(self, threshold=5):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "SELECT * FROM products WHERE quantity < ?",
#             (threshold,)
#         )
#         return cursor.fetchall()

#     def get_total_value(self):
#         cursor = self.conn.cursor()
#         cursor.execute("SELECT SUM(price * quantity) FROM products")
#         result = cursor.fetchone()[0]
#         return result if result else 0.0
    
#     def get_all_products(self):
#         cursor = self.conn.cursor()
#         cursor.execute("SELECT * FROM products")
#         rows = cursor.fetchall()
#         return [
#             {"id": r[0], "name": r[1], "price": r[2], 
#             "quantity": r[3], "supplier_id": r[4]}
#             for r in rows
#         ]

#     def find_product(self, product_id):
#         cursor = self.conn.cursor()
#         cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
#         row = cursor.fetchone()
#         if row is None:
#             return None
#         return {"id": row[0], "name": row[1], "price": row[2],
#                 "quantity": row[3], "supplier_id": row[4]}


# if __name__ == "__main__":
#     db = Database()
#     db.connect()

#     print(db.create_suppliers_table())
#     print(db.create_products_table())

#     print(db.add_supplier(1, "TechSource Ghana", "0244000001"))
#     print(db.add_supplier(2, "Accra Electronics", "0244000002"))

#     print(db.add_product(1001, "Laptop", 499.99, 30, supplier_id=1))
#     print(db.add_product(1002, "Mouse", 29.99, 2, supplier_id=1))
#     print(db.add_product(1003, "Keyboard", 49.99, 0, supplier_id=2))
#     print(db.add_product(1004, "Monitor", 299.99, 8, supplier_id=2))
#     print(db.add_product(1005, "Headphones", 89.99, 3))

#     print("\nProducts with Supplier Names:")
#     for row in db.get_products_with_suppliers():
#         print(row)

#     print("\nLow Stock Products:")
#     for row in db.get_low_stock():
#         print(row)

#     print(f"\nTotal Inventory Value: GHS {db.get_total_value():,.2f}")

#     db.disconnect()