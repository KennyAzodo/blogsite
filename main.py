from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
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


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Load user by ID


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        stmt = select(User).where(User.username == username)
        result = db.session.execute(stmt).scalar()
        password = request.form.get('password')
        if not result:
            flash('User is not registered, sign up!')
            return redirect(url_for('signup'))
        if password == result.password:
            login_user(result)
            return redirect(url_for('home'))
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
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html')


@app.route('/home')
def home():
    stmt = select(Post).where(Post.is_trending == True)
    result = db.session.execute(stmt).scalars().all()
    stmt2 = select(Post)  # Select all posts
    result2 = db.session.execute(stmt2)  # Execute the query
    posts = result2.scalars().all()
    return render_template('index.html', result=result, posts=posts, user=current_user)


@app.route('/create_post', methods=['GET', 'POST'])
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

        flash('Post created successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('create.html', form=form)

@app.route('/delete_post/<post_id>')
def delete(post_id):
    stmt = select(Post).where(Post.id == post_id)
    result = db.session.execute(stmt).scalar()
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)
