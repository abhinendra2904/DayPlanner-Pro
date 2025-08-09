from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Required for flash messages

# Simple in-memory task list (use DB for production)
scheduled_tasks = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        task_text = request.form.get("task_text")
        if not task_text.strip():
            flash("Task cannot be empty!", "danger")
            return redirect(url_for("index"))

        # Very basic parser: split by ' on ' and ' at '
        # In real app, replace with NLP or dateparser
        try:
            if " on " in task_text and " at " in task_text:
                task_part, rest = task_text.split(" on ", 1)
                date_part, time_part = rest.split(" at ", 1)
                task = {
                    "task": task_part.strip(),
                    "date": date_part.strip(),
                    "time": time_part.strip(),
                }
                # Check conflict
                for t in scheduled_tasks:
                    if t["date"] == task["date"] and t["time"] == task["time"]:
                        flash("⚠️ Conflict detected! Task at this date and time already exists.", "warning")
                        return redirect(url_for("index"))

                scheduled_tasks.append(task)
                flash("✅ Task scheduled successfully!", "success")
            else:
                flash("Please enter task in format: Task on YYYY-MM-DD at HH:MM", "warning")
        except Exception as e:
            flash(f"Error parsing task: {str(e)}", "danger")

        return redirect(url_for("index"))

    return render_template("index.html", tasks=scheduled_tasks)


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(scheduled_tasks):
        flash("Task not found!", "danger")
        return redirect(url_for("index"))

    task = scheduled_tasks[task_id]

    if request.method == "POST":
        new_text = request.form.get("task_text")
        if not new_text.strip():
            flash("Task cannot be empty!", "danger")
            return redirect(url_for("edit_task", task_id=task_id))

        try:
            if " on " in new_text and " at " in new_text:
                task_part, rest = new_text.split(" on ", 1)
                date_part, time_part = rest.split(" at ", 1)
                # Check conflict excluding current task
                for i, t in enumerate(scheduled_tasks):
                    if i != task_id and t["date"] == date_part.strip() and t["time"] == time_part.strip():
                        flash("⚠️ Conflict detected! Task at this date and time already exists.", "warning")
                        return redirect(url_for("edit_task", task_id=task_id))

                scheduled_tasks[task_id] = {
                    "task": task_part.strip(),
                    "date": date_part.strip(),
                    "time": time_part.strip(),
                }
                flash("✅ Task updated successfully!", "success")
                return redirect(url_for("index"))
            else:
                flash("Please enter task in format: Task on YYYY-MM-DD at HH:MM", "warning")
        except Exception as e:
            flash(f"Error parsing task: {str(e)}", "danger")

    return render_template("edit.html", task=task)


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if task_id < 0 or task_id >= len(scheduled_tasks):
        flash("Task not found!", "danger")
    else:
        scheduled_tasks.pop(task_id)
        flash("✅ Task deleted successfully!", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
