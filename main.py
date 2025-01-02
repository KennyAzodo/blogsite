from functools import wraps

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import mapped_column, Mapped
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_ckeditor import CKEditor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management
# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.init_app(app)
bootstrap = Bootstrap5(app)
login_manager.login_view = 'login'  # Redirect to 'login' view if not logged in

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'  # Replace with your database URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
ckeditor = CKEditor(app)


# Define a model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key column
    username: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)  # Unique username
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(120), nullable=False)  # User password

    # Relationship to Post model
    posts: Mapped[list['Post']] = db.relationship('Post', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key column
    title: Mapped[str] = mapped_column(db.String(120), nullable=False)
    subtitle: Mapped[str] = mapped_column(db.String(120), nullable=False)  # Post title
    content: Mapped[str] = mapped_column(db.Text, nullable=False)  # Post content
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'),
                                         nullable=False)  # Foreign key to User table
    is_trending: Mapped[bool] = mapped_column(db.Boolean, default=False,
                                              nullable=False)  # Indicates if the post is trending

    # Relationship to User model
    user: Mapped['User'] = db.relationship('User', back_populates='posts')

    def __repr__(self):
        return f'<Post {self.title}, Trending: {self.is_trending}>'


# Create the database tables
with app.app_context():
    db.create_all()


class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if not current_user.is_authenticated:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Load user by ID


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        stmt = select(User).where(User.username == username)
        result = db.session.execute(stmt).scalar()
        password = request.form.get('password')
        if not result:
            flash('User is not registered, sign up!')
            return redirect(url_for('signup'))
        if check_password_hash(result.password, password):
            login_user(result)
            return redirect(url_for('home'))
        elif not check_password_hash(result.password, password):
            flash('Password is incorrect')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if password != request.form.get('passwordconf'):
            flash('Passwords does not match')
            return redirect(url_for('signup'))
        stmt = select(User).where(User.username == username)
        result = db.session.execute(stmt).scalar()
        if result:
            flash('This username is not available')
            return redirect('signup')
        stmt2 = select(User).where(User.email == email)
        result2 = db.session.execute(stmt2).scalar()
        if result2:
            flash('This Email is already in use')
            return redirect('signup')
        new_user = User(username=username, email=email,
                        password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html')


@app.route('/')
def home():
    stmt = select(Post).where(Post.is_trending == True)
    result = db.session.execute(stmt).scalars().all()
    stmt2 = select(Post)  # Select all posts
    result2 = db.session.execute(stmt2)  # Execute the query
    posts = result2.scalars().all()
    return render_template('index.html', result=result, posts=posts, user=current_user, current_user=current_user)


@app.route('/create_post', methods=['GET', 'POST'])
@admin_only
def create_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        # Get data from the form
        title = form.title.data
        subtitle = form.subtitle.data
        body = form.body.data

        # Save to the database (example)
        new_post = Post(title=title, subtitle=subtitle, content=body, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('create.html', form=form)


@app.route('/delete_post/<post_id>')
@admin_only
def delete(post_id):
    stmt = select(Post).where(Post.id == post_id)
    result = db.session.execute(stmt).scalar()
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/read_more/<post_id>', methods=['GET', 'POST'])
def readmore(post_id):
    stmt = select(Post).where(Post.id == post_id)
    result = db.session.execute(stmt).scalar()
    return render_template('readmore.html', post=result)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/magazine')
def magazine():
    return render_template('magazine.html')

@app.route("/dashboard" ,methods=['GET','POST'])
def dashboard():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        conf_pass = request.form.get('passwordconf')

        stmt = select(Post).where(User.username == username)
        result = db.session.execute(stmt).scalar()
        if result:
            flash('USERNAME IS NOT AVAILABLE')
            return redirect(url_for('dashboard'))
        if len(username) < 1:
            flash('Username cannot be empty')
            return redirect(url_for('dashboard'))
        if len(email) < 1:
            flash('Email cannot be empty')
            return redirect(url_for('dashboard'))
        if len(password) < 1:
            flash('Password cannot be empty')
            return redirect(url_for('dashboard'))
        stmt2 = select(Post).where(User.email == email)
        result2 = db.session.execute(stmt2).scalar()
        if result2:
            flash('EMAIL HAS ALREADY BEEN REGISTERED')
            return redirect(url_for('dashboard'))
        if password != conf_pass:
            flash('Passwords does not match')
            return redirect(url_for('dashboard'))
        new_user = User(username=username, email=email,password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('createdashboard.html')



if __name__ == '__main__':
    app.run(debug=True)
