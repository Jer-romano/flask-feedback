from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
#See docs to learn how to set a good session key
app.config["SECRET_KEY"] = "My super secret Key"                                                  
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route("/")
def homepage():
    posts = Feedback.query.all()
    username = session.get("username", None)
    return render_template("home.html", username=username, posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        pw = form.password.data

        user = User.authenticate(username, pw)
        if user:
            session["username"] = user.username
            return redirect(f"/users/{username}")
        else:
            form.username.errors = ["Incorrect Username/Password"]
            return render_template("login.html", form=form)
    else:
        return render_template('login.html', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        pw = form.password.data
        email = form.email.data
        fname = form.first_name.data
        lname = form.last_name.data
        new_user = User.register(username=username, password=pw,
                                email=email, first_name=fname,
                                last_name=lname)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken. Please choose another")
            return render_template("base.html", form=form)
        session["username"] = new_user.username
        flash("Welcome! Your account has been created.", "success")
        return redirect(f"/users/{username}")
    
    else:
        return render_template('base.html', form=form)

@app.route("/feedback")
def main_feedback_page():
    return render_template('feedback.html')

@app.route("/secret")
def show_secrets():
    if 'username' not in session:
        flash("You must be logged in to view that page!", "danger")
        return redirect("/")
    return render_template('secret.html')

@app.route("/users/<username>")
def user_info(username):
    if session.get("username", None) == username:
        user = User.query.filter_by(username=username).first()
        return render_template("user_info.html", user=user)
    else:
        flash(f"You must be logged in as {username} to view that page!", "danger")
        return redirect("/")   

@app.route("/users/<username>/feedback/add", methods=["POST", "GET"])
def add_feedback(username):
    form = FeedbackForm()
    if session.get("username", None) == username:
        if form.validate_on_submit():
            user_tuple = db.session.query(User.id).filter(User.username == username).first()
            user_id = user_tuple[0]
            title = form.title.data
            content = form.content.data
            new_post = Feedback(title=title, content=content,
                                user_id=user_id)
            db.session.add(new_post)
            db.session.commit()
            return redirect(f"/users/{username}")
        else:
            return render_template("add_feedback.html", username=username,
                                        form=form)
    else:    
        flash(f"You must be logged in as {username} to view that page!", "danger")
        return redirect("/")

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def edit_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    username = feedback.author.username
    if session.get("username", None) == username:
        form = FeedbackForm(obj=feedback)
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.add(feedback)
            db.session.commit()
            return redirect(f"/users/{username}")
        else:
            return render_template("edit_feedback.html", form=form, feedback=feedback)
    else:    
        flash(f"You must be logged in as {feedback.username} to view that page!", "danger")
        return redirect("/")

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST", "GET"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    username = feedback.author.username
    if session.get("username", None) == username:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f"/users/{username}")
    else:    
        flash(f"You must be logged in as {feedback.username} to view that page!", "danger")
        return redirect("/")

@app.route("/users/<username>/delete", methods=["POST", "GET"])
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if session.get("username", None) == username:
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
    else:    
        flash(f"You must be logged in as {username} to perform that action!", "danger")
    return redirect("/")

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/")