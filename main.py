from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

#set up flask and database
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz2:12345@localhost:8889/blogz2'
app.config['SQLALCHEMY_ECHO'] = True

#create secret key in order for sessions to work s
app.secret_key = '#(47h68jv1)*JFLJCkjlfkds)($*)^$_'

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(480))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(120), unique=True)
  password = db.Column(db.String(120))
  #creates the relationship between a user and their posts
  blogs = db.relationship('Blog', backref='owner')

  #initalize the constructor - this connects the database to the webpage
  def __init__(self, username, password):
    self.username = username
    self.password = password

#verifies user has logged in before accessing the blog page
@app.before_request
def require_login():
    #create whitelist of pages where you don't need to be logged in to view
    allowed_routes = ['login', 'register','allusers', 'allblogs']
    # If the user has not logged in yet, i.e. there is not a key called 'username' in the session dictionary
    if request.endpoint not in allowed_routes and 'username' not in session:
      return render_template('home.html')


#login handler to render login page
@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    #retrieve the user with the given username in the database, if none exists it will return a none value.
    user = User.query.filter_by(username=username).first()
    #checks if user exists and also if it does, then it checks the password
    if user and user.password == password:
      #remember that the user has logged in, differentiates who is logged in by using cookies
      session['username'] = username
      flash("Login Successful")
      return redirect('/blog')

    else:
      flash("Username and/or Password were incorrect or not valid, please try again.")
      return redirect('/login')

  return render_template('login.html', title="Login")

#register handler to render register page
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        session['username'] = username
        session['logged_in'] = True

        if username == "" or username == " ":
            flash("Please enter a valid username")

        elif password == "" or password == " ":
            flash("Please create a password")

        elif password != verify:
            flash("Passwords do not match")

        elif password == "" and username == "":
            flash("Incomplete form, please fill out all fields.")

        else:
            existing_user = User.query.filter_by(username=username).first()

    #if user does not exist
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            username = session['username']
            flash("Thank you for registering to Blogz!")
            return redirect('/blog')

        else:
            flash("User already exists. Please log in or create a new account")

    return render_template('register.html', title="Register")

#logout user
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

#redirect to blog from index page
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('home.html')

#show all blogs
@app.route('/blog', methods=['POST', 'GET'])
def blog():

  #query all blogs by the user's id
    blog_id = request.args.get('id')

    if blog_id:
        post = Blog.query.get(blog_id)
        blogs = Blog.query.filter_by(id=blog_id).all()
        selected_post = Blog.query.filter_by(id=blog_id).first()
        return render_template('page.html', title=selected_post.title, blogs=blogs, post=post, selected_post=selected_post)

  #query by user ids
    user_id = request.args.get('user')

    if user_id:
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('selecteduser.html', title="Your Posts", blogs=blogs)

  #if no specific blog or user selected show all blogs
  # blogs = Blog.query.all()

    owner = User.query.filter_by(username=session['username']).first()
    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('blog.html', title="Blogz", blogs=blogs)


@app.route('/allblogs')
def allblogs():
    blogs = Blog.query.all()
    return render_template('allblogs.html', blogs=blogs, title="All Blogs")

@app.route('/allusers')
def allusers():
  users = User.query.all()
  return render_template('allusers.html', title="Blog Users", users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

  #Add a blog post
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']

    #check if posts is valid with all inputs entered
    if title == "" or title == " ":
      flash("Please enter a title for your new blog post")
      return redirect('/newpost')

    if body == "" or body == " ":
      flash("Please enter some content for new blog post")
      return redirect('/newpost')

    else:
      owner = User.query.filter_by(username=session['username']).first()
      new_blog = Blog(title, body, owner)

      db.session.add(new_blog)
      db.session.commit()

      flash("New blog successfully created")
      return redirect('/blog?id={0}'.format(new_blog.id))

  return render_template('newpost.html', title="Create a new blog")

#only run app if it is called in terminal
if __name__ == '__main__':
  app.run()
