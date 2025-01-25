from flask import Flask 
from flask import render_template, request, redirect, url_for
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database, relative to the app instance 
# folder. Also initialize the app with the extension. 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy()
db.init_app(app)

# Subclass the db.Model class in order to create declarative models.
# This is the main Task model we'll be using to model all our tasks.  
class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column() 
    completed: Mapped[bool] = mapped_column()

# Create the tables within the app context
with app.app_context(): 
    db.create_all()

# Basic error handling 
@app.errorhandler(404)
def page_not_found(error): 
    return render_template('page_not_found.html'), 404 

@app.errorhandler(401)
def unauthorized(error): 
    return render_template('unauthorized.html', 401)

# Flask will look for templates in the 
# templates/ folder by default. No need for additional specification. 
@app.route("/")
def index():
    tasks = db.session.query(Task).all()
    return render_template('index.html', tasks=tasks)

# Web applications use different HTTP methods when accessing URLs
# in our case we're always going to be POSTing a new task, so POST request here. 
@app.route("/add", methods=['POST'])
def add():
    new_task = Task(
        description=request.form['task-description'],
        completed=False,
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

@app.route("/delete/<int:id>", methods=['POST'])
def delete(id):
    task = db.get_or_404(Task, id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id): 
    if request.method == 'POST': 
        print("This is the id we're posting on", id)
        task = db.session.get(Task, id)
        task.description = request.form['task-description']
        db.session.commit()
        return redirect('/')
    else: 
        tasks = db.session.query(Task).all()
        return redirect('/')
    
# Persist 'checked' information across the requests. 
@app.route("/checked/<int:id>", methods=["GET", "POST"])
def checked(id):
    if request.method == 'POST': 
        task = db.session.get(Task, id)
        data = request.get_json()
        task.completed = data['checked']
        db.session.commit()
    return redirect('/')

# ~ Running the Application ~ 
#  
# flask --app app run 
# As a shortcut, since the app file is called app itself you 
# can omit the app and just do flask app run
# 
# <To run in debug mode>
# flask --app app run --debug