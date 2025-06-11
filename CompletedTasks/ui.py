# UI Class for a simple user interface

class UI:
    def __init__(self):
        self.menu_items = []

    def add_menu_item(self, item):
        self.menu_items.append(item)

    def display_menu(self):
        print("Menu:")
        for idx, item in enumerate(self.menu_items):
            print(f"{idx + 1}. {item}")

    def get_user_choice(self):
        choice = input("Enter your choice: ")
        return int(choice)

# Main function to test UI class
def main():
    ui = UI()
    ui.add_menu_item("Option 1")
    ui.add_menu_item("Option 2")
    ui.add_menu_item("Option 3")
    
    ui.display_menu()
    user_choice = ui.get_user_choice()
    print(f"User choice: {user_choice}")

if __name__ == "__main__":
    main()