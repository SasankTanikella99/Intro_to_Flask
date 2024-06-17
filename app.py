# Imports
from flask import Flask, render_template, redirect,request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


#My App
# name of the flask application is app
app = Flask(__name__)
Scss(app)


# configure SQLAlchemy connection
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

#context manager
with app.app_context():
    db.create_all()
    


#create a model
# Data class (row of data)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task{self.id}"


#defining a function for homepage, (creating a route for homepage)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        current_task = request.form.get('content', '')  # Use get() method with a default value
        if current_task.strip():  # Check if the task is not empty or whitespace
            new_task = Task(content=current_task)
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except Exception as e:
                db.session.rollback()  # Rollback the transaction if an error occurs
                return f"Error: {e}"
        else:
            # Handle the case when the 'content' field is empty or contains only whitespace
            error_message = "Please enter a valid task."
            tasks = Task.query.order_by(Task.created).all()
            return render_template("index.html", tasks=tasks, error=error_message)
    else:
        tasks = Task.query.order_by(Task.created).all()
        return render_template("index.html", tasks=tasks)


# delete item
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = Task.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"Error deleting:{e}"


#update item
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id:int):
    task = Task.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"Error updating:{e}"
    else:
        return render_template("edit.html", task=task)


# final test
if __name__ == "__main__":
    app.run(debug=True)