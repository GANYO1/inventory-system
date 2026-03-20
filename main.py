# main.py

from services.inventory_manager import InventoryManager


def main():
    manager = InventoryManager()

    print(manager.add_product(1001, "Laptop", 499.99, 30))
    print(manager.add_product(1002, "Mouse", 29.99, 2))
    print(manager.add_product(1003, "Keyboard", 49.99, 0))

    print(f"Total value: GHS {manager.get_total_value():,.2f}")

    low = manager.get_low_stock()
    print(f"Low stock items: {[p.name for p in low]}")

    print(manager.save())

    manager2 = InventoryManager()
    print(manager2.load())


if __name__ == "__main__":
    main()