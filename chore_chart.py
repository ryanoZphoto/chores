import json
from datetime import datetime, timedelta

DATA_FILE = 'chore_data.json' # File to save chore data
DAILY_CHORES_TO_RESET = [] # Chores that reset daily
BI_WEEKLY_CHORES_TO_RESET = [] # Chores that reset bi-weekly

def load_chores():
    """Loads chore data from a JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            chores_data = json.load(f)
            # Convert string dates back to datetime objects
            for chore in chores_data:
                if 'last_completed' in chore and chore['last_completed']:
                    chore['last_completed'] = datetime.fromisoformat(chore['last_completed'])
            return chores_data
    except FileNotFoundError:
        return [] # Return empty list if file doesn't exist
    except json.JSONDecodeError:
        print("Error reading chore data. Starting with an empty list.")
        return []

def save_chores(chores):
    """Saves chore data to a JSON file."""
    # Convert datetime objects to string for JSON serialization
    serializable_chores = []
    for chore in chores:
        temp_chore = chore.copy()
        if 'last_completed' in temp_chore and temp_chore['last_completed']:
            temp_chore['last_completed'] = temp_chore['last_completed'].isoformat()
        serializable_chores.append(temp_chore)
    with open(DATA_FILE, 'w') as f:
        json.dump(serializable_chores, f, indent=4)

def initialize_chores():
    """
    Sets up the initial list of chores with their values and frequencies.
    You can customize this list!
    """
    return [
        {"name": "Make Bed", "value": 10, "frequency": "daily", "last_completed": None},
        {"name": "Tidy Room (Clothes/Desk)", "value": 15, "frequency": "daily", "last_completed": None},
        {"name": "Load/Unload Dishwasher", "value": 20, "frequency": "daily", "last_completed": None},
        {"name": "Take Out Kitchen Trash", "value": 5, "frequency": "daily", "last_completed": None},

        {"name": "Clean His Bathroom (Toilet, Sink, Mirror)", "value": 50, "frequency": "weekly", "last_completed": None},
        {"name": "Vacuum Living Room", "value": 40, "frequency": "weekly", "last_completed": None},
        {"name": "Wipe Down Kitchen Counters/Stovetop", "value": 25, "frequency": "weekly", "last_completed": None},
        {"name": "Sort & Fold Own Laundry", "value": 30, "frequency": "weekly", "last_completed": None},

        {"name": "Sweep/Blow Front/Back Patios", "value": 35, "frequency": "bi-weekly", "last_completed": None},
        {"name": "Weed Small Front Garden Bed", "value": 60, "frequency": "bi-weekly", "last_completed": None},
        {"name": "Deep Clean Shower", "value": 75, "frequency": "bi-weekly", "last_completed": None},
        {"name": "Empty All House Trash Bins", "value": 30, "frequency": "bi-weekly", "last_completed": None},

        {"name": "Mow Front Lawn", "value": 100, "frequency": "monthly_or_ad_hoc", "last_completed": None},
        {"name": "Wash Car (Exterior)", "value": 80, "frequency": "monthly_or_ad_hoc", "last_completed": None},
        {"name": "Clean Out Refrigerator (Shelves)", "value": 90, "frequency": "monthly_or_ad_hoc", "last_completed": None},
        {"name": "Clean Garage (Sweep/Organize Area)", "value": 120, "frequency": "monthly_or_ad_hoc", "last_completed": None},
    ]

def display_chores(chores):
    """Displays the current list of chores."""
    print("\n--- Chore Chart ---")
    total_points_available = 0
    total_earned_points = 0

    if not chores:
        print("No chores currently defined. Add some!")
        return

    # Check for overdue/resettable chores for daily/bi-weekly resets
    today = datetime.now().date()
    current_week_number = today.isocalendar()[1] # Week number of the year

    print("\n--- Daily Chores ---")
    for i, chore in enumerate(chores):
        if chore['frequency'] == "daily":
            is_completed_today = False
            if chore['last_completed'] and chore['last_completed'].date() == today:
                is_completed_today = True
                total_earned_points += chore['value']
            
            status = "DONE" if is_completed_today else "PENDING"
            print(f"{i+1}. {chore['name']} ({chore['value']} pts) - Status: {status}")
            total_points_available += chore['value']

    print("\n--- Weekly Chores ---")
    for i, chore in enumerate(chores):
        if chore['frequency'] == "weekly":
            # Chores completed this week count
            is_completed_this_week = False
            if chore['last_completed'] and chore['last_completed'].isocalendar()[1] == current_week_number and chore['last_completed'].year == today.year:
                is_completed_this_week = True
                total_earned_points += chore['value']

            status = "DONE" if is_completed_this_week else "PENDING"
            last_done_str = chore['last_completed'].strftime('%Y-%m-%d') if chore['last_completed'] else "Never"
            print(f"{i+1}. {chore['name']} ({chore['value']} pts) - Last Done: {last_done_str} - Status: {status}")
            total_points_available += chore['value']

    print("\n--- Bi-Weekly Chores ---")
    for i, chore in enumerate(chores):
        if chore['frequency'] == "bi-weekly":
            # Simple check: if current week is odd/even, and it was done in that specific odd/even week
            # Or you can define specific reset dates for bi-weekly chores in the main script logic.
            # For simplicity, we'll just check if it was done recently enough based on current date.
            
            # Simple bi-weekly logic: If last_completed is within the last 14 days, consider it done.
            is_completed_recently = False
            if chore['last_completed'] and (today - chore['last_completed'].date()).days <= 14:
                is_completed_recently = True
                total_earned_points += chore['value']

            status = "DONE" if is_completed_recently else "PENDING"
            last_done_str = chore['last_completed'].strftime('%Y-%m-%d') if chore['last_completed'] else "Never"
            print(f"{i+1}. {chore['name']} ({chore['value']} pts) - Last Done: {last_done_str} - Status: {status}")
            total_points_available += chore['value']
    
    print("\n--- Monthly/Ad-Hoc Chores ---")
    for i, chore in enumerate(chores):
        if chore['frequency'] == "monthly_or_ad_hoc":
            last_done_str = chore['last_completed'].strftime('%Y-%m-%d') if chore['last_completed'] else "Never"
            print(f"{i+1}. {chore['name']} ({chore['value']} pts) - Last Done: {last_done_str}")
            # Ad-hoc chores are not 'pending' unless specifically assigned, so they don't contribute to 'available' points directly for general calculation,
            # but we can count them when completed.
            if chore['last_completed'] and chore['last_completed'].month == today.month and chore['last_completed'].year == today.year:
                 total_earned_points += chore['value']


    print("\n-------------------")
    print(f"Total Points Earned This Period: {total_earned_points}") # You'll define what "this period" means (e.g., current week, current month)
    print("-------------------\n")

def mark_chore_complete(chores):
    """Allows the user to mark a chore as complete."""
    display_chores(chores)
    while True:
        try:
            choice = int(input("Enter the number of the chore you completed (0 to go back): "))
            if choice == 0:
                return

            if 1 <= choice <= len(chores):
                selected_chore_index = choice - 1
                chore = chores[selected_chore_index]
                
                # Check if chore can be marked complete based on frequency (e.g., daily chores already done today)
                today = datetime.now().date()
                if chore['frequency'] == "daily" and chore['last_completed'] and chore['last_completed'].date() == today:
                    print(f"'{chore['name']}' has already been completed today. Choose another chore.")
                    continue
                
                # Bi-weekly check - optional, can be customized
                if chore['frequency'] == "bi-weekly":
                    if chore['last_completed'] and (today - chore['last_completed'].date()).days <= 14:
                         print(f"'{chore['name']}' was completed within the last two weeks. Choose another chore.")
                         continue


                chore['last_completed'] = datetime.now()
                print(f"'{chore['name']}' marked as complete! You earned {chore['value']} points.")
                save_chores(chores)
                break
            else:
                print("Invalid chore number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def add_new_chore(chores):
    """Allows adding a new chore."""
    name = input("Enter the new chore's name: ").strip()
    if not name:
        print("Chore name cannot be empty.")
        return

    try:
        value = int(input(f"Enter the point value for '{name}': "))
        if value <= 0:
            print("Point value must be positive.")
            return
    except ValueError:
        print("Invalid point value. Please enter a number.")
        return

    frequency_options = ["daily", "weekly", "bi-weekly", "monthly_or_ad_hoc"]
    frequency = ""
    while frequency not in frequency_options:
        frequency = input(f"Enter frequency ({', '.join(frequency_options)}): ").strip().lower()
        if frequency not in frequency_options:
            print("Invalid frequency. Please choose from the options.")

    chores.append({"name": name, "value": value, "frequency": frequency, "last_completed": None})
    save_chores(chores)
    print(f"'{name}' added successfully!")

def reset_chores_for_new_period(chores):
    """
    Resets "daily" chores at the start of a new day,
    "weekly" chores at the start of a new week (Monday),
    and "bi-weekly" chores every other week.
    This function should ideally be run once per day/week by you.
    """
    today = datetime.now().date()
    current_week_number = today.isocalendar()[1] # Week number of the year

    print("\nChecking for chores to reset...")
    chores_reset_count = 0
    for chore in chores:
        # Daily reset: if last completed was not today, it's pending again
        if chore['frequency'] == "daily":
            if chore['last_completed'] and chore['last_completed'].date() < today:
                # No actual reset needed, it's just 'pending' again in the display logic.
                # We can add it to a list if we want to confirm a visual reset.
                pass 
            elif not chore['last_completed']: # If never completed, it's always pending
                pass

        # Weekly reset: if last completed was in a previous week, it's pending again
        if chore['frequency'] == "weekly":
            if chore['last_completed'] and (chore['last_completed'].isocalendar()[1] != current_week_number or chore['last_completed'].year < today.year):
                # Resetting 'last_completed' to None means it's available again for points this week.
                # We could set it to the start of the current week for more nuanced tracking if needed.
                # For simplicity, we just leave it if it was done this week, otherwise it's effectively "reset"
                pass 
            elif not chore['last_completed']:
                pass
                
        # Bi-weekly reset: more complex. Let's make it simple.
        # If the last_completed date is older than 14 days, it's "reset".
        # Or, we can have a global flag/specific date for when bi-weekly chores should be available.
        # For this simplified version, the display function determines if it's "pending" based on last_completed.
        # The true "reset" is often just marking it complete, and the system waits till next period.
        
        # This function primarily serves to inform you if a new period has started.
        # The main display and mark complete logic handles if points are earned.
        pass # No explicit resetting of 'last_completed' in this function to avoid losing history.
    
    print("Reset check complete. Display will reflect current status.")
    # For a true "reset" that clears 'last_completed' for *all* daily/weekly/bi-weekly chores
    # at a specific time (e.g., midnight Sunday for weekly, midnight daily for daily),
    # you'd need a more advanced scheduler (outside this simple script's scope).
    # For now, the 'display_chores' logic and 'mark_chore_complete' prevents double-counting.
    save_chores(chores) # Save any implicit changes, though none explicitly made here.


def main():
    """Main function to run the chore chart program."""
    chores = load_chores()

    # If no chores are loaded (first run or file error), initialize them
    if not chores:
        chores = initialize_chores()
        save_chores(chores) # Save initial chores

    # A simple way to handle daily/weekly resets: you manually trigger it.
    # In a real application, this would run automatically at specific times.
    reset_chores_for_new_period(chores) 

    while True:
        print("\n--- Main Menu ---")
        print("1. View Chores")
        print("2. Mark Chore Complete")
        print("3. Add New Chore")
        print("4. Exit")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            display_chores(chores)
        elif choice == '2':
            mark_chore_complete(chores)
        elif choice == '3':
            add_new_chore(chores)
        elif choice == '4':
            print("Exiting Chore Chart. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()