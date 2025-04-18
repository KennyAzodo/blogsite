from functools import wraps

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func, Integer, Text
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import mapped_column, Mapped, relationship
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_ckeditor import CKEditor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
from flask_gravatar import Gravatar

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
gravatar = Gravatar(app,
                    size=40,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# Define a model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key column
    username: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)  # Unique username
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(120), nullable=False)  # User password
    is_admin: Mapped[bool] = mapped_column(db.Boolean, default=False,
                                           nullable=False)
    # Relationship to Post model
    posts: Mapped[list['Post']] = db.relationship('Post', back_populates='user', cascade='all, delete-orphan')
    comments = relationship("Comment", back_populates="comment_author")
    likes: Mapped[list['Like']] = db.relationship('Like', back_populates='user', cascade='all, delete-orphan')

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
                                              nullable=False)
    # Relationship to User model
    user: Mapped['User'] = db.relationship('User', back_populates='posts')
    comments = relationship("Comment", back_populates="parent_post")
    likes: Mapped[list['Like']] = db.relationship('Like', back_populates='post', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.title}, Trending: {self.is_trending}>'


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationship with the User model
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    # Relationship with the Post model
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("posts.id"))
    parent_post = relationship("Post", back_populates="comments")


class Like(db.Model):
    __tablename__ = 'likes'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    user = relationship('User', backref='liked_posts')
    post = relationship('Post', backref='post_likes')

    def __repr__(self):
        return f'<Like User {self.user_id} Post {self.post_id}>'


# Create the database tables
with app.app_context():
    db.create_all()


class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    comment_text = CKEditorField('Comment', validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is authenticated and an admin
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            # Abort with 403 error if not an admin
            return abort(403)
        # Otherwise, continue with the route function
        return f(*args, **kwargs)

    return decorated_function


def mainadmin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is authenticated and an admin
        if not current_user.id == 1:
            # Abort with 403 error if not an admin
            return abort(403)
        # Otherwise, continue with the route function
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
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        # Check if the username is already taken
        stmt = select(User).where(User.username == username)
        result = db.session.execute(stmt).scalar()
        if result:
            flash('This username is not available')
            return redirect(url_for('signup'))

        # Check if the email is already in use
        stmt2 = select(User).where(User.email == email)
        result2 = db.session.execute(stmt2).scalar()
        if result2:
            flash('This email is already in use')
            return redirect(url_for('signup'))

        # Check if this is the first user using `select`
        stmt_count = select(func.count(User.id))
        user_count = db.session.execute(stmt_count).scalar()
        is_admin = user_count == 0

        # Create a new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8),
            is_admin=is_admin
        )
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

    stmt2 = select(Comment).where(Comment.post_id == post_id)
    result2 = db.session.execute(stmt2).scalars().all()  # Get all comments related to the post
    if result2:
        for comment in result2:
            db.session.delete(comment)  # Delete each comment individually
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/read_more/<post_id>', methods=['GET', 'POST'])
def readmore(post_id):
    stmt = select(Post).where(Post.id == post_id)
    result = db.session.execute(stmt).scalar()
    comment = CommentForm()

    if comment.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        # Ensure that the post_id is properly set when creating the comment
        new_comment = Comment(
            text=comment.comment_text.data,
            comment_author=current_user,
            parent_post=result,  # This automatically sets post_id
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template('readmore.html', post=result, comment=comment)


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


@app.route("/dashboard", methods=['GET', 'POST'])
@mainadmin_only
def dashboard():
    if request.method == 'POST':
        email = request.form.get('email')

        # Query the user by email
        stmt = select(User).where(User.email == email)
        user = db.session.execute(stmt).scalar()

        # Check if the user exists
        if not user:
            flash('Email is not registered')
            return redirect(url_for('dashboard'))

        # Make the user an admin
        user.is_admin = True
        db.session.commit()
        flash(f"{user.username} has been successfully made an admin!")
        return redirect(url_for('dashboard'))

    return render_template('createdashboard.html')


@app.route('/like/<int:post_id>', methods=['GET', 'POST'])
@login_required
def like_post(post_id):
    stmt = select(Post).where(Post.id == post_id)
    post = db.session.execute(stmt).scalar()

    if not post:
        flash('Post not found!')
        return redirect(url_for('home'))

    # Option 1: Increment the like count
    # post.likes += 1

    # Option 2: Add a new like record
    existing_like_stmt = select(Like).where(Like.user_id == current_user.id, Like.post_id == post_id)
    existing_like = db.session.execute(existing_like_stmt).scalar()
    if existing_like:
        db.session.delete(existing_like)

    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)

    db.session.commit()
    return redirect(url_for('home'))


@app.route('/manageadmin')
@mainadmin_only
def manage_admin():
    # Query to select all admin users
    stmt_admins = select(User).where(User.is_admin == True)
    admins = db.session.execute(stmt_admins).scalars().all()

    # Query to select all non-admin users
    stmt_non_admins = select(User).where(User.is_admin == False)
    non_admins = db.session.execute(stmt_non_admins).scalars().all()

    return render_template('manageadmin.html', admins=admins, non_admins=non_admins)


@app.route('/delete_user/<int:user_id>', methods=['GET','POST'])
@mainadmin_only
def delete_user(user_id):
    if request.method == 'POST':
        stmt = select(User).where(User.id == user_id)
        user = db.session.execute(stmt).scalar()
        if user.id == current_user.id:
            flash('User cannot delete this account')
            return redirect(url_for('manage_admin'))
        elif user:
            db.session.delete(user)
            db.session.commit()
    return redirect(url_for('manage_admin'))




if __name__ == '__main__':
    app.run(debug=True)
