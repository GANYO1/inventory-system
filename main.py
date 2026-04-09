# This is the entry point of the application — the file you run directly
# It ties everything together by using the InventoryManager service
# Think of it as the "front door" of your system
# Nothing imports from this file — it imports from everything else

# Import the InventoryManager class from the services folder
# This gives us access to all inventory operations —
# adding products, getting low stock, saving, loading etc
from services.inventory_manager import InventoryManager


def main():
    # This function contains all the startup logic for the application
    # Wrapping everything in a function keeps the code organised
    # and prevents it from running when imported by another file

    # Create a new InventoryManager instance
    # This starts with an empty inventory list
    # The default filename "data/inventory.json" is used for saving and loading
    manager = InventoryManager()

    # Add three products to the inventory
    # Each call creates a Product instance and appends it to manager.inventory
    # print() displays the success message returned by add_product
    print(manager.add_product(1001, "Laptop", 499.99, 30))
    print(manager.add_product(1002, "Mouse", 29.99, 2))
    print(manager.add_product(1003, "Keyboard", 49.99, 0))

    # Calculate and print the total monetary value of all stock
    # get_total_value() loops through all products and sums price * quantity
    # :,.2f formats the number with commas and 2 decimal places
    # Example output: Total value: GHS 15,059.68
    print(f"Total value: GHS {manager.get_total_value():,.2f}")

    # Get all products where quantity is below the default threshold of 5
    # Returns a list of Product instances
    low = manager.get_low_stock()

    # [p.name for p in low] is a list comprehension
    # It loops through each low stock Product instance and extracts just the name
    # Result is a simple list of names like ['Mouse', 'Keyboard']
    print(f"Low stock items: {[p.name for p in low]}")

    # Save the current inventory to data/inventory.json
    # Converts each Product instance to a dictionary using to_dict()
    # then writes the list of dictionaries to the JSON file
    # print() displays the success message returned by save()
    print(manager.save())

    # Create a second InventoryManager instance with an empty inventory
    # This simulates what happens when the program restarts
    # manager2 starts fresh — nothing in its inventory list yet
    manager2 = InventoryManager()

    # Load the inventory from the JSON file into manager2
    # Reads the file, converts each dictionary back into a Product instance
    # and populates manager2.inventory with those instances
    # print() displays how many products were loaded
    print(manager2.load())


# This guard ensures main() only runs when you execute this file directly
# with: py main.py
# If another file imports from main.py this block is skipped
# Without this guard, main() would run automatically every time this file is imported
# which would cause unexpected behaviour
if __name__ == "__main__":
    main()




# from services.inventory_manager import InventoryManager


# def main():
#     manager = InventoryManager()

#     print(manager.add_product(1001, "Laptop", 499.99, 30))
#     print(manager.add_product(1002, "Mouse", 29.99, 2))
#     print(manager.add_product(1003, "Keyboard", 49.99, 0))

#     print(f"Total value: GHS {manager.get_total_value():,.2f}")

#     low = manager.get_low_stock()
#     print(f"Low stock items: {[p.name for p in low]}")

#     print(manager.save())

#     manager2 = InventoryManager()
#     print(manager2.load())


# if __name__ == "__main__":
#     main()