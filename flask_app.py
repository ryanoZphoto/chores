import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import unquote_plus, quote_plus

app = Flask(__name__)

DATA_FILE = 'chore_data.json' # File to save chore data

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
    except (FileNotFoundError, json.JSONDecodeError):
        # If file not found or corrupted, initialize with default chores
        return initialize_chores()

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
        {"name": "Make Bed", "value": 10, "frequency": "daily", "last_completed": None, "instructions": "Make sure sheets are straight, pillows are fluffed, and blanket is neat."},
        {"name": "Tidy Room (Clothes/Desk)", "value": 15, "frequency": "daily", "last_completed": None, "instructions": "Put away all clothes, clear surfaces, put trash in bin."},
        {"name": "Load/Unload Dishwasher", "value": 20, "frequency": "daily", "last_completed": None, "instructions": "Scrape plates, load dishes neatly, run if full."},
        {"name": "Take Out Kitchen Trash", "value": 5, "frequency": "daily", "last_completed": None, "instructions": "Tie bag, take to outside bin, replace kitchen bag."},

        {"name": "Clean His Bathroom (Toilet, Sink, Mirror)", "value": 50, "frequency": "weekly", "last_completed": None, "instructions": "Thoroughly wipe down toilet, sink, counter, and mirror."},
        {"name": "Vacuum Living Room", "value": 40, "frequency": "weekly", "last_completed": None, "instructions": "Clear floor of clutter, vacuum thoroughly, empty canister."},
        {"name": "Wipe Down Kitchen Counters/Stovetop", "value": 25, "frequency": "weekly", "last_completed": None, "instructions": "Use all-purpose cleaner."},
        {"name": "Sort & Fold Own Laundry", "value": 30, "frequency": "weekly", "last_completed": None, "instructions": "Sort by colors/types, fold neatly, put away in drawers."},

        {"name": "Sweep/Blow Front/Back Patios", "value": 35, "frequency": "bi-weekly", "last_completed": None, "instructions": "Sweep away leaves, dirt, and cobwebs from designated patios."},
        {"name": "Weed Small Front Garden Bed", "value": 60, "frequency": "bi-weekly", "last_completed": None, "instructions": "Focus on the small garden bed near the mailbox. Pull weeds by the root."},
        {"name": "Deep Clean Shower", "value": 75, "frequency": "bi-weekly", "last_completed": None, "instructions": "Thoroughly scrub shower walls, floor, and glass. Use appropriate cleaner."},
        {"name": "Empty All House Trash Bins", "value": 30, "frequency": "bi-weekly", "last_completed": None, "instructions": "Empty all small trash cans in bedrooms, bathrooms, office. Replace liners."},

        {"name": "Mow Front Lawn", "value": 100, "frequency": "ad_hoc", "last_completed": None, "instructions": "Mow the front lawn carefully. Ask for help with edges if needed. (Requires adult supervision)."},
        {"name": "Wash Car (Exterior)", "value": 80, "frequency": "ad_hoc", "last_completed": None, "instructions": "Soap, rinse, and dry car exterior."},
        {"name": "Clean Out Refrigerator (Shelves)", "value": 90, "frequency": "ad_hoc", "last_completed": None, "instructions": "Remove items, wipe down one shelf section thoroughly. (Rotate section each time)."},
        {"name": "Clean Garage (Sweep/Organize Area)", "value": 120, "frequency": "ad_hoc", "last_completed": None, "instructions": "Sweep entire garage floor, organize a designated section of the garage."},
    ]

def get_chore_status(chore):
    """Determines the status of a chore based on its frequency and last_completed date."""
    today = datetime.now().date()
    current_week_number = today.isocalendar()[1]
    
    if chore['frequency'] == "daily":
        if chore['last_completed'] and chore['last_completed'].date() == today:
            return "DONE"
        else:
            return "PENDING"
    elif chore['frequency'] == "weekly":
        if chore['last_completed'] and chore['last_completed'].isocalendar()[1] == current_week_number and chore['last_completed'].year == today.year:
            return "DONE"
        else:
            return "PENDING"
    elif chore['frequency'] == "bi-weekly":
        # Simple bi-weekly logic: done if completed in the last 14 days
        if chore['last_completed'] and (today - chore['last_completed'].date()).days <= 14:
            return "DONE"
        else:
            return "PENDING"
    elif chore['frequency'] == "ad_hoc":
        # Ad-hoc chores are just displayed with their last completion date
        return "Not Recurring"
    return "Unknown"

def calculate_points(chores):
    """Calculates points earned for chores completed in the current relevant period."""
    today = datetime.now().date()
    current_week_number = today.isocalendar()[1]
    total_points_earned = 0

    for chore in chores:
        status = get_chore_status(chore)
        if status == "DONE":
            total_points_earned += chore['value']
        elif chore['frequency'] == "ad_hoc" and chore['last_completed'] and chore['last_completed'].month == today.month and chore['last_completed'].year == today.year:
             total_points_earned += chore['value'] # Count ad-hoc if done this month

    return total_points_earned

@app.route('/')
def index():
    chores = load_chores()
    
    # Categorize chores for display
    daily_chores = [c for c in chores if c['frequency'] == 'daily']
    weekly_chores = [c for c in chores if c['frequency'] == 'weekly']
    bi_weekly_chores = [c for c in chores if c['frequency'] == 'bi-weekly']
    ad_hoc_chores = [c for c in chores if c['frequency'] == 'ad_hoc']

    # Update status for display
    for chore_list in [daily_chores, weekly_chores, bi_weekly_chores, ad_hoc_chores]:
        for chore in chore_list:
            chore['display_status'] = get_chore_status(chore)
            chore['display_last_completed'] = chore['last_completed'].strftime('%Y-%m-%d') if chore['last_completed'] else "Never"
    
    points_earned = calculate_points(chores)

    return render_template('index.html', 
                           daily_chores=daily_chores,
                           weekly_chores=weekly_chores,
                           bi_weekly_chores=bi_weekly_chores,
                           ad_hoc_chores=ad_hoc_chores,
                           points_earned=points_earned)

@app.route('/complete/<path:chore_name>')
def complete_chore(chore_name):
    # Decode the URL-encoded chore name
    decoded_chore_name = unquote_plus(chore_name)
    print(f"Attempting to complete chore: {decoded_chore_name}")
    
    chores = load_chores()
    today = datetime.now().date()
    
    for chore in chores:
        if chore['name'] == decoded_chore_name:
            current_status = get_chore_status(chore)
            if current_status == "DONE":
                print(f"Chore '{decoded_chore_name}' is already done for its current period.")
            else:
                chore['last_completed'] = today.strftime('%Y-%m-%d')
                save_chores(chores)
                print(f"Chore '{decoded_chore_name}' marked complete!")
            break
    
    return redirect(url_for('index'))

# To run this directly without `flask run`:
if __name__ == '__main__':
    # Initialize chores if data file doesn't exist or is empty/corrupted
    chores = load_chores()
    if not chores: # If load_chores returned empty (meaning it initialized new ones)
        save_chores(initialize_chores())
    
    app.run()