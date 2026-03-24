import sqlite3

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0
        )
    """)
    return "Products table ready"


def add_product(conn, id, name, price, quantity):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (id, name, price, quantity) VALUES (?, ?, ?, ?)",
        (id, name, price, quantity)
    )
    return f"Added {name} to database"


def get_all_products(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()


def update_quantity(conn, id, new_quantity):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, id)
    )
    return f"Updated quantity for product {id}"


def get_low_stock(conn, threshold=5):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE quantity < ?",
        (threshold,)
    )
    return cursor.fetchall()


if __name__ == "__main__":
    conn = sqlite3.connect("data/inventory.db")

    print(create_table(conn))

    print(add_product(conn, 1001, "Laptop", 499.99, 30))
    print(add_product(conn, 1002, "Mouse", 29.99, 2))
    print(add_product(conn, 1003, "Keyboard", 49.99, 0))
    print(add_product(conn, 1004, "Monitor", 299.99, 8))

    print("\nAll products:")
    for row in get_all_products(conn):
        print(row)

    print("\nUpdating Laptop quantity...")
    print(update_quantity(conn, 1001, 25))

    print("\nLow stock products:")
    for row in get_low_stock(conn):
        print(row)

conn.commit()
conn.close()