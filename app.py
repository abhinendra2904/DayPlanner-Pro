from flask import Flask, render_template, request, redirect, url_for, flash
import re
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

scheduled_tasks = []

def mock_nlp_parse(text):
    time_match = re.search(r'(\d{1,2})(:\d{2})?\s?(AM|PM)?', text, re.IGNORECASE)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)[1:]) if time_match.group(2) else 0
        meridian = time_match.group(3)
        if meridian and meridian.upper() == 'PM' and hour != 12:
            hour += 12
        elif meridian and meridian.upper() == 'AM' and hour == 12:
            hour = 0
        time_str = f"{hour:02d}:{minute:02d}"
    else:
        time_str = "09:00"

    if 'tomorrow' in text.lower():
        date_obj = datetime.now() + timedelta(days=1)
    elif 'next week' in text.lower():
        date_obj = datetime.now() + timedelta(days=7)
    else:
        date_obj = datetime.now()

    date_str = date_obj.strftime("%Y-%m-%d")

    task = re.sub(r'(\d{1,2})(:\d{2})?\s?(AM|PM)?', '', text, flags=re.IGNORECASE)
    task = re.sub(r'\b(tomorrow|next week)\b', '', task, flags=re.IGNORECASE)
    task = task.strip().strip('"').strip("'")

    return {
        "task": task,
        "date": date_str,
        "time": time_str
    }

def check_conflict(new_task, exclude_index=None):
    for i, t in enumerate(scheduled_tasks):
        if i == exclude_index:
            continue
        if t['date'] == new_task['date'] and t['time'] == new_task['time']:
            return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_text = request.form.get('task_text')
        if not task_text:
            flash("Please enter a task.", "warning")
            return redirect(url_for('index'))

        parsed_task = mock_nlp_parse(task_text)
        if check_conflict(parsed_task):
            flash(f"Conflict detected! You already have a task at {parsed_task['time']} on {parsed_task['date']}.", "danger")
        else:
            scheduled_tasks.append(parsed_task)
            flash(f"Task scheduled: '{parsed_task['task']}' on {parsed_task['date']} at {parsed_task['time']}", "success")

        return redirect(url_for('index'))

    return render_template('index.html', tasks=scheduled_tasks)

# Route to show the edit form
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(scheduled_tasks):
        flash("Task not found.", "danger")
        return redirect(url_for('index'))

    task = scheduled_tasks[task_id]

    if request.method == 'POST':
        new_text = request.form.get('task_text')
        if not new_text:
            flash("Please enter a task.", "warning")
            return redirect(url_for('edit_task', task_id=task_id))

        new_parsed_task = mock_nlp_parse(new_text)
        if check_conflict(new_parsed_task, exclude_index=task_id):
            flash(f"Conflict detected! You already have a task at {new_parsed_task['time']} on {new_parsed_task['date']}.", "danger")
            return redirect(url_for('edit_task', task_id=task_id))

        scheduled_tasks[task_id] = new_parsed_task
        flash("Task updated successfully.", "success")
        return redirect(url_for('index'))

    return render_template('edit.html', task=task, task_id=task_id)

# Route to delete a task
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if task_id < 0 or task_id >= len(scheduled_tasks):
        flash("Task not found.", "danger")
    else:
        scheduled_tasks.pop(task_id)
        flash("Task deleted successfully.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

