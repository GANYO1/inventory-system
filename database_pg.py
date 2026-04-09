# database_pg.py
# This file contains the Database class — the data access layer of your system
# It handles all communication between your application and the PostgreSQL database
# No other file should write SQL directly — all database operations go through here
# This is called separation of concerns — one file, one responsibility

# psycopg2 is the Python driver for PostgreSQL
# It allows Python to speak to a PostgreSQL database
import psycopg2

# os lets us read environment variables
# Used to get the DATABASE_URL without hardcoding it in the code
import os

# load_dotenv reads the .env file and loads its contents as environment variables
# Without this, os.getenv("DATABASE_URL") would return None
from dotenv import load_dotenv

# Actually load the .env file into memory
# This must be called before any os.getenv() calls
load_dotenv()


class Database:

    def __init__(self):
        # Constructor — runs when you create a new Database instance
        # self.conn stores the database connection
        # Set to None initially because we haven't connected yet
        # connect() must be called separately before any database operations
        self.conn = None

    def disconnect(self):
        # Safely closes the database connection
        # The "if self.conn" check prevents errors if disconnect is called
        # when there is no active connection
        if self.conn:
            # Commit any pending changes before closing
            # This ensures no data is lost if commit wasn't called explicitly
            self.conn.commit()

            # Close the actual connection to the PostgreSQL server
            # This frees up the connection slot on the database server
            self.conn.close()

            # Set conn back to None so we know there's no active connection
            self.conn = None

    def connect(self):
        # Opens a connection to the PostgreSQL database
        # Reads the connection URL from the DATABASE_URL environment variable
        # The URL contains everything needed — host, port, username, password, database name

        self.conn = psycopg2.connect(
            # os.getenv reads DATABASE_URL from the .env file
            # This keeps credentials out of the code — never hardcode passwords
            os.getenv("DATABASE_URL"),

            # sslmode="require" forces an encrypted connection
            # Required by Neon and most cloud PostgreSQL providers for security
            sslmode="require"
        )
        # Return self so connect() can be chained if needed
        # Example: db = Database().connect()
        return self

    def create_suppliers_table(self):
        # Creates the suppliers table in the database if it doesn't already exist
        # IF NOT EXISTS prevents an error if the table was already created before

        # cursor is the object that executes SQL commands
        # Think of conn as the phone line and cursor as your voice
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,        -- unique identifier, no duplicates allowed
                name TEXT NOT NULL,            -- supplier name is required
                phone TEXT                     -- phone is optional, can be NULL
            )
        """)

        # Save the table creation to the database permanently
        # Without commit the change exists temporarily and disappears when connection closes
        self.conn.commit()
        return "Suppliers table ready"

    def create_products_table(self):
        # Creates the products table in the database if it doesn't already exist
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,         -- unique product identifier
                name TEXT NOT NULL,             -- product name is required
                price REAL NOT NULL,            -- price is required, REAL allows decimals
                quantity INTEGER NOT NULL DEFAULT 0,  -- quantity required, defaults to 0 if not provided
                supplier_id INTEGER,            -- optional, links to a supplier
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                -- FOREIGN KEY means supplier_id must exist in the suppliers table
                -- This enforces data integrity — you can't link to a supplier that doesn't exist
            )
        """)
        self.conn.commit()
        return "Products table ready"

    def add_supplier(self, id, name, phone):
        # Inserts a new supplier into the suppliers table
        cursor = self.conn.cursor()

        cursor.execute(
            # %s are placeholders — never put variables directly in SQL strings
            # This prevents SQL injection attacks where malicious input could destroy your database
            "INSERT INTO suppliers (id, name, phone) VALUES (%s, %s, %s)",

            # The actual values are passed as a separate tuple
            # psycopg2 handles the safe substitution of %s with these values
            (id, name, phone)
        )
        self.conn.commit()
        return f"Added supplier {name}"

    def add_product(self, id, name, price, quantity, supplier_id=None):
        # Inserts a new product into the products table
        # supplier_id=None means it's optional — a product can exist without a supplier
        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO products (id, name, price, quantity, supplier_id) VALUES (%s, %s, %s, %s, %s)",
            # Five values matching the five %s placeholders in the SQL above
            # supplier_id can be None — PostgreSQL stores this as NULL
            (id, name, price, quantity, supplier_id)
        )
        self.conn.commit()
        return f"Added product {name}"

    def get_all_products(self):
        # Retrieves every product from the database
        # Returns a list of dictionaries — one dictionary per product
        cursor = self.conn.cursor()

        # SELECT * means return all columns for every row
        cursor.execute("SELECT * FROM products")

        # fetchall() retrieves all matching rows at once
        # Each row is a tuple: (1001, 'Laptop', 499.99, 30, 1)
        rows = cursor.fetchall()

        # Convert each tuple into a readable dictionary
        # r[0] is the first column (id), r[1] is second (name), and so on
        # This makes the data easier to work with and return as JSON
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
            # WHERE filters rows — only return the product with this specific ID
            "SELECT * FROM products WHERE id = %s",
            # product_id is passed as a tuple (product_id,)
            # The comma makes it a tuple — required by psycopg2 even for one value
            (product_id,)
        )

        # fetchone() retrieves only the first matching row
        # Returns None if no row matched the WHERE condition
        row = cursor.fetchone()

        if row is None:
            # No product found with that ID — return None
            # The caller must check for None before using the result
            return None

        # Product found — convert the tuple to a dictionary and return it
        return {
            "id": row[0], "name": row[1], "price": row[2],
            "quantity": row[3], "supplier_id": row[4]
        }

    def get_low_stock(self, threshold=5):
        # Returns all products where quantity is below the threshold
        # threshold=5 is the default — products with less than 5 units are low stock
        cursor = self.conn.cursor()

        cursor.execute(
            # WHERE quantity < %s filters only products below the threshold
            "SELECT * FROM products WHERE quantity < %s",
            (threshold,)
        )

        # Return all matching rows as a list of tuples
        # Each tuple: (id, name, price, quantity, supplier_id)
        return cursor.fetchall()

    def get_total_value(self):
        # Calculates the total monetary value of all stock in the database
        # Uses SQL SUM() aggregate function — faster than fetching all rows and calculating in Python
        cursor = self.conn.cursor()

        # SUM(price * quantity) multiplies price by quantity for each row
        # then adds all results together into a single number
        cursor.execute("SELECT SUM(price * quantity) FROM products")

        # fetchone() returns one row — the result of the SUM calculation
        # [0] gets the first (and only) value from that row
        result = cursor.fetchone()[0]

        # If the products table is empty SUM returns NULL which becomes None in Python
        # Return 0.0 instead of None to avoid errors when formatting the number
        return result if result else 0.0

    def get_products_with_suppliers(self):
        # Returns each product paired with its supplier name
        # Uses a JOIN to combine data from two tables in one query
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT products.name, suppliers.name
            FROM products
            -- LEFT JOIN includes all products even if they have no supplier
            -- Products without a supplier will show NULL for the supplier name
            LEFT JOIN suppliers ON products.supplier_id = suppliers.id
        """)

        # Return all rows — each row is a tuple: (product_name, supplier_name)
        return cursor.fetchall()

    def create_users_table(self):
        # Creates the users table for authentication
        # Stores registered usernames and their hashed passwords
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,          -- SERIAL means PostgreSQL auto-generates the next ID
                                                -- You don't pass an ID when creating a user
                username TEXT UNIQUE NOT NULL,  -- UNIQUE prevents two users with the same username
                                                -- NOT NULL means username is required
                hashed_password TEXT NOT NULL   -- Stores the bcrypt hash — never the real password
            )
        """)
        self.conn.commit()
        return "Users table ready"

    def create_user(self, username, hashed_password):
        # Inserts a new user into the users table
        # hashed_password is already hashed before this method is called
        # This method never sees or stores plain text passwords
        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
            # id is not included — SERIAL handles it automatically
            (username, hashed_password)
        )
        self.conn.commit()
        return f"User {username} created"

    def get_user(self, username):
        # Looks up a user by username
        # Used during login to find the stored hashed password
        # Returns a dictionary if found, None if not found
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )

        # fetchone() gets the first matching row — usernames are unique so at most one row matches
        row = cursor.fetchone()

        if row is None:
            # No user found with that username
            return None

        # User found — return as a dictionary
        # row[0] = id, row[1] = username, row[2] = hashed_password
        return {"id": row[0], "username": row[1], "hashed_password": row[2]}


# This block only runs when you execute database_pg.py directly
# It does NOT run when api.py imports from this file
# Used for testing the database layer independently
if __name__ == "__main__":
    # Create a Database instance and connect to PostgreSQL
    db = Database()
    db.connect()

    # Create all three tables — IF NOT EXISTS means safe to run multiple times
    print(db.create_suppliers_table())
    print(db.create_products_table())
    print(db.create_users_table())

    # Insert two suppliers
    print(db.add_supplier(1, "TechSource Ghana", "0244000001"))
    print(db.add_supplier(2, "Accra Electronics", "0244000002"))

    # Insert five products — some linked to suppliers, one without
    print(db.add_product(1001, "Laptop", 499.99, 30, 1))
    print(db.add_product(1002, "Mouse", 29.99, 2, 1))
    print(db.add_product(1003, "Keyboard", 49.99, 0, 2))
    print(db.add_product(1004, "Monitor", 299.99, 8, 2))
    print(db.add_product(1005, "Headphones", 89.99, 3, None))

    # Print all products to confirm they were inserted correctly
    print("\nAll products:")
    for p in db.get_all_products():
        print(p)

    # Print total inventory value formatted with commas and 2 decimal places
    print(f"\nTotal value: GHS {db.get_total_value():,.2f}")

    # Close the connection — always disconnect when done
    db.disconnect()




#     import psycopg2
# import os
# from dotenv import load_dotenv

# load_dotenv()


# class Database:
#     def __init__(self):
#         self.conn = None
        
#     def disconnect(self):
#         if self.conn:
#             self.conn.commit()
#             self.conn.close()
#             self.conn = None

#     def connect(self):
#         self.conn = psycopg2.connect(
#             os.getenv("DATABASE_URL"),
#             sslmode="require"
#     )
#         return self

#     def create_suppliers_table(self):
#         cursor = self.conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS suppliers (
#                 id INTEGER PRIMARY KEY,
#                 name TEXT NOT NULL,
#                 phone TEXT
#             )
#         """)
#         self.conn.commit()
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
#         self.conn.commit()
#         return "Products table ready"

#     def add_supplier(self, id, name, phone):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "INSERT INTO suppliers (id, name, phone) VALUES (%s, %s, %s)",
#             (id, name, phone)
#         )
#         self.conn.commit()
#         return f"Added supplier {name}"

#     def add_product(self, id, name, price, quantity, supplier_id=None):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "INSERT INTO products (id, name, price, quantity, supplier_id) VALUES (%s, %s, %s, %s, %s)",
#             (id, name, price, quantity, supplier_id)
#         )
#         self.conn.commit()
#         return f"Added product {name}"

#     def get_all_products(self):
#         cursor = self.conn.cursor()
#         cursor.execute("SELECT * FROM products")
#         rows = cursor.fetchall()
#         return [
#             {"id": r[0], "name": r[1], "price": r[2],
#              "quantity": r[3], "supplier_id": r[4]}
#             for r in rows
#         ]

#     def find_product(self, product_id):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "SELECT * FROM products WHERE id = %s",
#             (product_id,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return None
#         return {
#             "id": row[0], "name": row[1], "price": row[2],
#             "quantity": row[3], "supplier_id": row[4]
#         }

#     def get_low_stock(self, threshold=5):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "SELECT * FROM products WHERE quantity < %s",
#             (threshold,)
#         )
#         return cursor.fetchall()

#     def get_total_value(self):
#         cursor = self.conn.cursor()
#         cursor.execute("SELECT SUM(price * quantity) FROM products")
#         result = cursor.fetchone()[0]
#         return result if result else 0.0

#     def get_products_with_suppliers(self):
#         cursor = self.conn.cursor()
#         cursor.execute("""
#             SELECT products.name, suppliers.name
#             FROM products
#             LEFT JOIN suppliers ON products.supplier_id = suppliers.id
#         """)
#         return cursor.fetchall()
    

#     def create_users_table(self):
#         cursor = self.conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id SERIAL PRIMARY KEY,
#                 username TEXT UNIQUE NOT NULL,
#                 hashed_password TEXT NOT NULL
#             )
#         """)
#         self.conn.commit()
#         return "Users table ready"
    

#     def create_user(self, username, hashed_password):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
#             (username, hashed_password)
#         )
#         self.conn.commit()
#         return f"User {username} created"
    

#     def get_user(self, username):
#         cursor = self.conn.cursor()
#         cursor.execute(
#             "SELECT * FROM users WHERE username = %s",
#             (username,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return None
#         return {"id": row[0], "username": row[1], "hashed_password": row[2]}   
    

# if __name__ == "__main__":
#     db = Database()
#     db.connect()

#     print(db.create_suppliers_table())
#     print(db.create_products_table())
#     print(db.create_users_table())

#     print(db.add_supplier(1, "TechSource Ghana", "0244000001"))
#     print(db.add_supplier(2, "Accra Electronics", "0244000002"))

#     print(db.add_product(1001, "Laptop", 499.99, 30, 1))
#     print(db.add_product(1002, "Mouse", 29.99, 2, 1))
#     print(db.add_product(1003, "Keyboard", 49.99, 0, 2))
#     print(db.add_product(1004, "Monitor", 299.99, 8, 2))
#     print(db.add_product(1005, "Headphones", 89.99, 3, None))

#     print("\nAll products:")
#     for p in db.get_all_products():
#         print(p)

#     print(f"\nTotal value: GHS {db.get_total_value():,.2f}")

#     db.disconnect()
