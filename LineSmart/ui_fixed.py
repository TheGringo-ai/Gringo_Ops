Here is the corrected code with the specified changes:

```python
def main_menu():
    print("Main Menu")
    print("1 - Task 1")
    print("2 - Task 2")
    print("3 - Exit")

choice = input("Please select an option (1-3): ")

if choice.isdigit() and int(choice) in [1, 2, 3]:
    if int(choice) == 1:
        # Task 1 implementation here
        pass
    elif int(choice) == 2:
        # Task 2 implementation here
        pass
    elif int(choice) == 3:
        print("Exiting...")
        exit()
else:
    print("Invalid input. Please select a number between 1 and 3.")
```