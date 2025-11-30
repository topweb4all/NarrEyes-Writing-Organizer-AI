from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'project.db'

# ==================== Database Functions ====================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all tables"""
    with app.app_context():
        db = get_db()

        # Users table
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Characters table
        db.execute('''CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            role TEXT,
            description TEXT,
            personality TEXT,
            background TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')

        # Chapters table
        db.execute('''CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            chapter_number INTEGER NOT NULL,
            content TEXT,
            word_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')

        # Timeline table
        db.execute('''CREATE TABLE IF NOT EXISTS timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_title TEXT NOT NULL,
            event_date TEXT,
            description TEXT,
            chapter_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
        )''')

        # Relationships table
        db.execute('''CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            character1_id INTEGER NOT NULL,
            character2_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (character1_id) REFERENCES characters(id) ON DELETE CASCADE,
            FOREIGN KEY (character2_id) REFERENCES characters(id) ON DELETE CASCADE
        )''')

        # Create indexes
        db.execute('CREATE INDEX IF NOT EXISTS idx_characters_user ON characters(user_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_chapters_user ON chapters(user_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_timeline_user ON timeline(user_id)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_relationships_user ON relationships(user_id)')

        db.commit()
        db.close()
        print("✅ Database initialized successfully")

# ==================== Decorators ====================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Authentication Routes ====================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            # Validation
            if not all([username, email, password, confirm_password]):
                flash('All fields are required', 'warning')
                return redirect(url_for('register'))

            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('register'))

            if len(password) < 6:
                flash('Password must be at least 6 characters', 'warning')
                return redirect(url_for('register'))

            # Hash password
            password_hash = generate_password_hash(password)

            # Insert into database
            db = get_db()
            try:
                db.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                          (username, email, password_hash))
                db.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username or email already exists', 'danger')
            finally:
                db.close()

        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')
            print(f"❌ Registration Error: {e}")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                flash('Please enter username and password', 'warning')
                return redirect(url_for('login'))

            db = get_db()
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            db.close()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')

        except Exception as e:
            flash('An error occurred during login', 'danger')
            print(f"❌ Login Error: {e}")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('index'))

# ==================== Dashboard ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    db = get_db()

    characters_count = db.execute('SELECT COUNT(*) as count FROM characters WHERE user_id = ?',
                                  (session['user_id'],)).fetchone()['count']
    chapters_count = db.execute('SELECT COUNT(*) as count FROM chapters WHERE user_id = ?',
                                (session['user_id'],)).fetchone()['count']
    timeline_count = db.execute('SELECT COUNT(*) as count FROM timeline WHERE user_id = ?',
                                (session['user_id'],)).fetchone()['count']

    db.close()

    return render_template('dashboard.html',
                          characters_count=characters_count,
                          chapters_count=chapters_count,
                          timeline_count=timeline_count)

# ==================== Characters Routes ====================

@app.route('/characters')
@login_required
def characters():
    """List all characters"""
    db = get_db()
    characters_list = db.execute('SELECT * FROM characters WHERE user_id = ? ORDER BY created_at DESC',
                                 (session['user_id'],)).fetchall()
    db.close()
    return render_template('characters.html', characters=characters_list)

@app.route('/add_character', methods=['GET', 'POST'])
@login_required
def add_character():
    """Add new character"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        role = request.form.get('role')
        description = request.form.get('description')
        personality = request.form.get('personality')
        background = request.form.get('background')

        if not name:
            flash('Character name is required', 'warning')
            return redirect(url_for('add_character'))

        db = get_db()
        db.execute('''INSERT INTO characters
                     (user_id, name, age, role, description, personality, background)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], name, age, role, description, personality, background))
        db.commit()
        db.close()

        flash('Character added successfully!', 'success')
        return redirect(url_for('characters'))

    return render_template('add_character.html')

@app.route('/edit_character/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_character(id):
    """Edit character"""
    db = get_db()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        role = request.form.get('role')
        description = request.form.get('description')
        personality = request.form.get('personality')
        background = request.form.get('background')

        db.execute('''UPDATE characters
                     SET name=?, age=?, role=?, description=?, personality=?, background=?
                     WHERE id=? AND user_id=?''',
                  (name, age, role, description, personality, background, id, session['user_id']))
        db.commit()
        db.close()

        flash('Character updated successfully!', 'success')
        return redirect(url_for('characters'))

    character = db.execute('SELECT * FROM characters WHERE id=? AND user_id=?',
                          (id, session['user_id'])).fetchone()
    db.close()

    if not character:
        flash('Character not found', 'danger')
        return redirect(url_for('characters'))

    return render_template('edit_character.html', character=character)

@app.route('/delete_character/<int:id>')
@login_required
def delete_character(id):
    """Delete character"""
    db = get_db()
    db.execute('DELETE FROM characters WHERE id=? AND user_id=?', (id, session['user_id']))
    db.commit()
    db.close()

    flash('Character deleted successfully!', 'success')
    return redirect(url_for('characters'))

# ==================== Chapters Routes ====================

@app.route('/chapters')
@login_required
def chapters():
    """List all chapters"""
    db = get_db()
    chapters_list = db.execute('SELECT * FROM chapters WHERE user_id = ? ORDER BY chapter_number',
                               (session['user_id'],)).fetchall()
    db.close()
    return render_template('chapters.html', chapters=chapters_list)

@app.route('/add_chapter', methods=['GET', 'POST'])
@login_required
def add_chapter():
    """Add new chapter"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        chapter_number = request.form.get('chapter_number')
        content = request.form.get('content', '')
        word_count = len(content.split()) if content else 0
        status = request.form.get('status', 'draft')

        if not title or not chapter_number:
            flash('Title and chapter number are required', 'warning')
            return redirect(url_for('add_chapter'))

        db = get_db()
        db.execute('''INSERT INTO chapters
                     (user_id, title, chapter_number, content, word_count, status)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], title, chapter_number, content, word_count, status))
        db.commit()
        db.close()

        flash('Chapter added successfully!', 'success')
        return redirect(url_for('chapters'))

    return render_template('add_chapter.html')

@app.route('/chapter/<int:id>')
@login_required
def chapter_detail(id):
    """View chapter details"""
    db = get_db()
    chapter = db.execute('SELECT * FROM chapters WHERE id=? AND user_id=?',
                        (id, session['user_id'])).fetchone()
    db.close()

    if not chapter:
        flash('Chapter not found', 'danger')
        return redirect(url_for('chapters'))

    return render_template('chapter_detail.html', chapter=chapter)

@app.route('/edit_chapter/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(id):
    """Edit chapter"""
    db = get_db()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        chapter_number = request.form.get('chapter_number')
        content = request.form.get('content', '')
        word_count = len(content.split()) if content else 0
        status = request.form.get('status', 'draft')

        db.execute('''UPDATE chapters
                     SET title=?, chapter_number=?, content=?, word_count=?, status=?,
                         updated_at=CURRENT_TIMESTAMP
                     WHERE id=? AND user_id=?''',
                  (title, chapter_number, content, word_count, status, id, session['user_id']))
        db.commit()
        db.close()

        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('chapter_detail', id=id))

    chapter = db.execute('SELECT * FROM chapters WHERE id=? AND user_id=?',
                        (id, session['user_id'])).fetchone()
    db.close()

    if not chapter:
        flash('Chapter not found', 'danger')
        return redirect(url_for('chapters'))

    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/delete_chapter/<int:id>')
@login_required
def delete_chapter(id):
    """Delete chapter"""
    db = get_db()
    db.execute('DELETE FROM chapters WHERE id=? AND user_id=?', (id, session['user_id']))
    db.commit()
    db.close()

    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('chapters'))

# ==================== Timeline Routes ====================

@app.route('/timeline')
@login_required
def timeline():
    """View timeline"""
    db = get_db()
    events = db.execute('''SELECT t.*, c.title as chapter_title
                          FROM timeline t
                          LEFT JOIN chapters c ON t.chapter_id = c.id
                          WHERE t.user_id = ?
                          ORDER BY t.event_date''',
                       (session['user_id'],)).fetchall()
    db.close()
    return render_template('timeline.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    """Add timeline event"""
    if request.method == 'POST':
        event_title = request.form.get('event_title', '').strip()
        event_date = request.form.get('event_date')
        description = request.form.get('description')
        chapter_id = request.form.get('chapter_id')

        if not event_title:
            flash('Event title is required', 'warning')
            return redirect(url_for('add_event'))

        db = get_db()
        db.execute('''INSERT INTO timeline
                     (user_id, event_title, event_date, description, chapter_id)
                     VALUES (?, ?, ?, ?, ?)''',
                  (session['user_id'], event_title, event_date, description, chapter_id))
        db.commit()
        db.close()

        flash('Event added successfully!', 'success')
        return redirect(url_for('timeline'))

    db = get_db()
    chapters_list = db.execute('SELECT id, title, chapter_number FROM chapters WHERE user_id = ?',
                               (session['user_id'],)).fetchall()
    db.close()

    return render_template('add_event.html', chapters=chapters_list)

@app.route('/delete_event/<int:id>')
@login_required
def delete_event(id):
    """Delete event"""
    db = get_db()
    db.execute('DELETE FROM timeline WHERE id=? AND user_id=?', (id, session['user_id']))
    db.commit()
    db.close()

    flash('Event deleted successfully!', 'success')
    return redirect(url_for('timeline'))

# ==================== Relationships Routes ====================

@app.route('/relationships')
@login_required
def relationships():
    """View relationships"""
    db = get_db()
    relationships_list = db.execute('''SELECT r.*,
                                      c1.name as character1_name,
                                      c2.name as character2_name
                                      FROM relationships r
                                      JOIN characters c1 ON r.character1_id = c1.id
                                      JOIN characters c2 ON r.character2_id = c2.id
                                      WHERE r.user_id = ?
                                      ORDER BY r.created_at DESC''',
                                   (session['user_id'],)).fetchall()
    db.close()
    return render_template('relationships.html', relationships=relationships_list)

@app.route('/add_relationship', methods=['GET', 'POST'])
@login_required
def add_relationship():
    """Add character relationship"""
    if request.method == 'POST':
        character1_id = request.form.get('character1_id')
        character2_id = request.form.get('character2_id')
        relationship_type = request.form.get('relationship_type', '').strip()
        description = request.form.get('description')

        if not all([character1_id, character2_id, relationship_type]):
            flash('All fields are required', 'warning')
            return redirect(url_for('add_relationship'))

        if character1_id == character2_id:
            flash('Cannot create relationship with the same character', 'danger')
            return redirect(url_for('add_relationship'))

        db = get_db()
        db.execute('''INSERT INTO relationships
                     (user_id, character1_id, character2_id, relationship_type, description)
                     VALUES (?, ?, ?, ?, ?)''',
                  (session['user_id'], character1_id, character2_id, relationship_type, description))
        db.commit()
        db.close()

        flash('Relationship added successfully!', 'success')
        return redirect(url_for('relationships'))

    db = get_db()
    characters_list = db.execute('SELECT id, name FROM characters WHERE user_id = ?',
                                 (session['user_id'],)).fetchall()
    db.close()

    return render_template('add_relationship.html', characters=characters_list)

@app.route('/delete_relationship/<int:id>')
@login_required
def delete_relationship(id):
    """Delete relationship"""
    db = get_db()
    db.execute('DELETE FROM relationships WHERE id=? AND user_id=?', (id, session['user_id']))
    db.commit()
    db.close()

    flash('Relationship deleted successfully!', 'success')
    return redirect(url_for('relationships'))

# ==================== AI Generator Route ====================

@app.route('/ai', methods=['GET', 'POST'])
@login_required
def ai():
    """AI content generator"""
    if request.method == 'POST':
        prompt = request.form.get('prompt', '').strip()
        ai_type = request.form.get('ai_type', 'character')

        if not prompt:
            flash('Please enter a prompt', 'warning')
            return render_template('ai.html')

        result = generate_ai_content(prompt, ai_type)

        return render_template('ai.html', result=result, prompt=prompt, ai_type=ai_type)

    return render_template('ai.html')

def generate_ai_content(prompt, ai_type):
    """Generate AI content using OpenRouter"""
    try:
        import requests

        API_URL = "https://openrouter.ai/api/v1/chat/completions"
        API_KEY = "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"  # 👈 Add your key

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "NarrEyes",
            "Content-Type": "application/json"
        }

        # Best models for each type
        models = {
            'character': 'meta-llama/llama-4-maverick:free',
            'scene': 'google/gemini-2.0-flash-exp:free',
            'dialogue': 'mistralai/mistral-nemo-instruct:free',
            'description': 'meta-llama/llama-3.1-70b-instruct:free'
        }

        # System instructions
        instructions = {
            'character': "You are a character development expert. Create detailed, realistic character descriptions with personality, background, and motivations.",
            'scene': "You are a scene-setting expert. Write vivid, immersive scenes using sensory details and atmosphere.",
            'dialogue': "You are a dialogue coach. Write natural, engaging conversations that reveal character.",
            'description': "You are a descriptive writer. Create rich, detailed descriptions with vivid imagery."
        }

        payload = {
            "model": models.get(ai_type, 'meta-llama/llama-4-maverick:free'),
            "messages": [
                {"role": "system", "content": instructions.get(ai_type, "You are a creative writing assistant.")},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 800,
            "top_p": 0.92
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        elif response.status_code == 503:
            return "⏳ Model is loading. Please wait 30-60 seconds and try again."
        elif response.status_code == 402:
            return "💳 OpenRouter credits exhausted. Please use free models."
        elif response.status_code == 401:
            return "❌ Invalid API Key. Check your OpenRouter key."
        else:
            return f"❌ Error {response.status_code}"

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==================== Helper Function ====================

def create_test_user():
    """Create test user for debugging"""
    db = get_db()
    try:
        existing = db.execute('SELECT * FROM users WHERE username = ?', ('test',)).fetchone()
        if not existing:
            password_hash = generate_password_hash('test123')
            db.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                      ('test', 'test@narreyes.com', password_hash))
            db.commit()
            print("✅ Test user created - username: 'test', password: 'test123'")
    except:
        pass
    finally:
        db.close()

        # ==================== Profile/Account Routes ====================

@app.route('/profile')
@login_required
def profile():
    """View user profile"""
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    # Get user statistics
    stats = {
        'characters': db.execute('SELECT COUNT(*) as count FROM characters WHERE user_id = ?',
                                (session['user_id'],)).fetchone()['count'],
        'chapters': db.execute('SELECT COUNT(*) as count FROM chapters WHERE user_id = ?',
                              (session['user_id'],)).fetchone()['count'],
        'words': db.execute('SELECT SUM(word_count) as total FROM chapters WHERE user_id = ?',
                           (session['user_id'],)).fetchone()['total'] or 0,
        'timeline': db.execute('SELECT COUNT(*) as count FROM timeline WHERE user_id = ?',
                              (session['user_id'],)).fetchone()['count'],
        'relationships': db.execute('SELECT COUNT(*) as count FROM relationships WHERE user_id = ?',
                                   (session['user_id'],)).fetchone()['count']
    }

    db.close()
    return render_template('profile.html', user=user, stats=stats)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()

            if not username or not email:
                flash('Username and email are required', 'warning')
                return redirect(url_for('edit_profile'))

            db = get_db()

            # Check if username/email already exists (excluding current user)
            existing = db.execute('''SELECT id FROM users
                                    WHERE (username = ? OR email = ?) AND id != ?''',
                                 (username, email, session['user_id'])).fetchone()

            if existing:
                flash('Username or email already taken', 'danger')
                db.close()
                return redirect(url_for('edit_profile'))

            # Update user info
            db.execute('UPDATE users SET username = ?, email = ? WHERE id = ?',
                      (username, email, session['user_id']))
            db.commit()
            db.close()

            # Update session
            session['username'] = username

            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))

        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'danger')
            print(f"❌ Profile Update Error: {e}")

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()

    return render_template('edit_profile.html', user=user)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not all([current_password, new_password, confirm_password]):
                flash('All fields are required', 'warning')
                return redirect(url_for('change_password'))

            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return redirect(url_for('change_password'))

            if len(new_password) < 6:
                flash('Password must be at least 6 characters', 'warning')
                return redirect(url_for('change_password'))

            # Verify current password
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

            if not check_password_hash(user['password_hash'], current_password):
                flash('Current password is incorrect', 'danger')
                db.close()
                return redirect(url_for('change_password'))

            # Update password
            new_password_hash = generate_password_hash(new_password)
            db.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                      (new_password_hash, session['user_id']))
            db.commit()
            db.close()

            flash('Password changed successfully!', 'success')
            return redirect(url_for('profile'))

        except Exception as e:
            flash(f'Error changing password: {str(e)}', 'danger')
            print(f"❌ Password Change Error: {e}")

    return render_template('change_password.html')

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    try:
        password = request.form.get('password', '')

        if not password:
            flash('Password is required to delete account', 'warning')
            return redirect(url_for('profile'))

        # Verify password
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

        if not check_password_hash(user['password_hash'], password):
            flash('Incorrect password', 'danger')
            db.close()
            return redirect(url_for('profile'))

        # Delete all user data
        db.execute('DELETE FROM relationships WHERE user_id = ?', (session['user_id'],))
        db.execute('DELETE FROM timeline WHERE user_id = ?', (session['user_id'],))
        db.execute('DELETE FROM chapters WHERE user_id = ?', (session['user_id'],))
        db.execute('DELETE FROM characters WHERE user_id = ?', (session['user_id'],))
        db.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
        db.commit()
        db.close()

        # Clear session
        username = session.get('username', 'User')
        session.clear()

        flash(f'Account deleted. Goodbye, {username}!', 'info')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'danger')
        print(f"❌ Account Deletion Error: {e}")
        return redirect(url_for('profile'))

# ==================== Run Application ====================

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Create test user
    create_test_user()

    # Print startup message
    print("\n" + "="*60)
    print("  🚀 NarrEyes Writing Assistant")
    print("="*60)
    print("  📍 Server: http://localhost:5000")
    print("  📍 Local:  http://127.0.0.1:5000")
    print("="*60)
    print("  👤 Test Login:")
    print("     Username: test")
    print("     Password: test123")
    print("="*60)
    print("  Press CTRL+C to stop")
    print("="*60 + "\n")

    # Run app
    app.run(host='0.0.0.0', port=5000, debug=True)
