from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError
import random
from flask import session

# Flask App Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    languages = db.relationship('Language', backref='user', lazy=True)

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    words = db.relationship('Word', backref='language', lazy=True)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(100), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

# Forms
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("Username already exists. Choose another.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class AddWordForm(FlaskForm):
    language = SelectField("Language", choices=[], coerce=int)
    original = StringField(validators=[InputRequired()], render_kw={"placeholder": "Word"})
    translation = StringField(validators=[InputRequired()], render_kw={"placeholder": "Translation"})
    submit = SubmitField("Add Word")

class TestForm(FlaskForm):
    answer = StringField(validators=[InputRequired()], render_kw={"placeholder": "Your answer"})
    submit = SubmitField("Submit Answer")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    selected_language_id = session.get('selected_language')
    if not selected_language_id:
        return redirect(url_for('select_language'))
    
    selected_language = Language.query.get(selected_language_id)
    if not selected_language or selected_language.user_id != current_user.id:
        flash("Invalid language selected.", "danger")
        session.pop('selected_language', None)
        return redirect(url_for('select_language'))

    return render_template(
        'dashboard.html',
        selected_language=selected_language,
    )


@app.route('/add-language', methods=['POST'])
@login_required
def add_language():
    language_name = request.form.get('language_name')
    if language_name:
        new_language = Language(name=language_name, user_id=current_user.id)
        db.session.add(new_language)
        db.session.commit()
        flash("Language added successfully!", "success")
    else:
        flash("Language name cannot be empty.", "danger")
    return redirect(url_for('select_language'))


@app.route('/select-language', methods=['GET', 'POST'])
@login_required
def select_language():
    user_languages = Language.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        selected_language_id = request.form.get('language')
        if selected_language_id:
            session['selected_language'] = selected_language_id
            return redirect(url_for('dashboard'))
        flash("Please select a language or add a new one.", "warning")
    
    return render_template('select_language.html', user_languages=user_languages)


@app.route('/add-word', methods=['GET', 'POST'])
@login_required
def add_word():
    selected_language_id = session.get('selected_language')
    if not selected_language_id:
        return redirect(url_for('select_language'))

    form = AddWordForm()

    # Załaduj dostępne języki tylko dla zalogowanego użytkownika
    form.language.choices = [(lang.id, lang.name) for lang in Language.query.filter_by(user_id=current_user.id).all()]

    # Ustaw domyślny język na podstawie wybranego z sesji
    form.language.data = int(selected_language_id)

    if form.validate_on_submit():
        # Sprawdź, czy dane słowo już istnieje w wybranym języku
        existing_word = Word.query.filter_by(
            original=form.original.data,
            language_id=form.language.data
        ).first()

        if existing_word:
            flash("This word already exists in the selected language.", "error")
            return render_template('add_word.html', form=form)

        # Jeśli słowo nie istnieje, dodaj nowe
        new_word = Word(
            original=form.original.data,
            translation=form.translation.data,
            language_id=form.language.data
        )
        db.session.add(new_word)
        db.session.commit()
        flash("Word added successfully!", "success")
        return redirect(url_for('dashboard'))

    # Debugowanie błędów formularza, jeśli wystąpią
    if form.errors:
        print(form.errors)

    return render_template('add_word.html', form=form)


@app.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    form = TestForm()

    # Pobierz ID wybranego języka z sesji
    selected_language_id = session.get('selected_language')
    if not selected_language_id:
        flash("Please select a language first.", "warning")
        return redirect(url_for('select_language'))

    # Pobierz język i jego słowa
    selected_language = Language.query.get(selected_language_id)
    language_name = selected_language.name if selected_language else "Unknown"
    words = Word.query.filter_by(language_id=selected_language_id).all()

    if not words:
        flash("You don't have any words to test in the selected language.", "warning")
        return redirect(url_for('dashboard'))

    # Zainicjalizuj postęp, jeśli jeszcze go nie ma
    if 'progress' not in session:
        session['progress'] = []

    progress = session['progress']

    # Filtruj słowa, które jeszcze nie zostały odpowiedziane
    remaining_words = [word for word in words if word.id not in progress]

    # Sprawdź, czy są jeszcze słowa do testowania
    if not remaining_words:
        session.pop('progress', None)  # Usuń postęp po zakończeniu testu
        return render_template(
            'test.html',
            form=form,
            word=None,
            progress_percentage=100,
            correct_count=len(progress),
            total_words=len(words),
            remaining=0,
            language_name=language_name,
            test_completed=True  
        )

    # Pobierz ID słowa z sesji lub wylosuj nowe słowo
    current_word_id = session.get('current_word_id')
    if current_word_id:
        word = next((w for w in remaining_words if w.id == current_word_id), None)
    else:
        word = random.choice(remaining_words)
        session['current_word_id'] = word.id

    if form.validate_on_submit():
        # Normalizacja odpowiedzi użytkownika i poprawnego tłumaczenia
        user_answer = form.answer.data.strip().lower()
        correct_answer = word.translation.strip().lower()

        if user_answer == correct_answer:
            flash("Correct!", "success")
            progress.append(word.id)
            session['progress'] = progress
            session.pop('current_word_id', None)  # Usuń bieżące słowo po udzieleniu odpowiedzi
        else:
            flash(f"Wrong! The correct translation is '{word.translation}'.", "danger")

        # Przeładuj stronę, aby wyświetlić nowe słowo
        return redirect(url_for('test'))

    # Oblicz postęp
    total_words = len(words)
    correct_count = len(progress)
    progress_percentage = (correct_count / total_words) * 100

    return render_template(
        'test.html',
        form=form,
        word=word,
        progress_percentage=progress_percentage,
        correct_count=correct_count,
        total_words=total_words,
        remaining=len(remaining_words),
        language_name=language_name,
        test_completed=False  
    )



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('index'))


# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
