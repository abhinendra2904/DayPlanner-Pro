import re
from datetime import datetime, timedelta

# Mock NLP parsing function (simple rule-based)
def mock_nlp_parse(text):
    # Simple regex to find time (e.g., 3 PM, 15:00)
    time_match = re.search(r'(\d{1,2})(:\d{2})?\s?(AM|PM)?', text, re.IGNORECASE)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)[1:]) if time_match.group(2) else 0
        meridian = time_match.group(3)
        if meridian and meridian.upper() == 'PM' and hour != 12:
            hour += 12
        elif meridian and meridian.upper() == 'AM' and hour == 12:
            hour = 0
         = f"{hour:02d}:{minute:02d}"
    else:
        time_str = "09:00"  # Default time if none found

    # Simple date parsing (look for 'tomorrow' or 'next week')
    if 'tomorrow' in text.lower():
        date_obj = datetime.now() + timedelta(days=1)
    elif 'next week' in text.lower():
        date_obj = datetime.now() + timedelta(days=7)
    else:
        date_obj = datetime.now()

    date_str = date_obj.strftime("%Y-%m-%d")

    # Extract task description by removing time and date words
    task = re.sub(r'(\d{1,2})(:\d{2})?\s?(AM|PM)?', '', text, flags=re.IGNORECASE)
    task = re.sub(r'\b(tomorrow|next week)\b', '', task, flags=re.IGNORECASE)
    task = task.strip()

    return {
        "task": task,
        "date": date_str,
        "time": time_str
    }

# Function to simulate scheduling conflict check
def check_conflict(existing_tasks, new_task):
    for t in existing_tasks:
        if t['date'] == new_task['date'] and t['time'] == new_task['time']:
            return True
    return False

# Main program simulation
def main():
    scheduled_tasks = []

    while True:
        user_input = input("Enter your task (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        parsed_task = mock_nlp_parse(user_input)
        conflict = check_conflict(scheduled_tasks, parsed_task)

        if conflict:
            print(f"⚠️ Conflict detected! You already have a task at {parsed_task['time']} on {parsed_task['date']}.")
            reschedule = input("Would you like to enter a different time? (yes/no): ")
            if reschedule.lower() == 'yes':
                continue
            else:
                print("Task not scheduled.")
                continue

        scheduled_tasks.append(parsed_task)
        print(f"✅ Task scheduled: '{parsed_task['task']}' on {parsed_task['date']} at {parsed_task['time']}")

    print("\nYour scheduled tasks:")
    for t in scheduled_tasks:
        print(f"- {t['task']} at {t['time']} on {t['date']}")

if __name__ == "__main__":
    main()
