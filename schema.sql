-- حذف الجداول القديمة إذا كانت موجودة
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS timeline;
DROP TABLE IF EXISTS chapters;
DROP TABLE IF EXISTS characters;
DROP TABLE IF EXISTS users;

-- جدول المستخدمين
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول الشخصيات
CREATE TABLE characters (
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
);

-- جدول الفصول
CREATE TABLE chapters (
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
);

-- جدول الأحداث (Timeline)
CREATE TABLE timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_title TEXT NOT NULL,
    event_date TEXT,
    description TEXT,
    chapter_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

-- جدول العلاقات بين الشخصيات
CREATE TABLE relationships (
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
);

-- إنشاء Indexes لتحسين الأداء
CREATE INDEX idx_characters_user_id ON characters(user_id);
CREATE INDEX idx_chapters_user_id ON chapters(user_id);
CREATE INDEX idx_chapters_number ON chapters(chapter_number);
CREATE INDEX idx_timeline_user_id ON timeline(user_id);
CREATE INDEX idx_timeline_chapter_id ON timeline(chapter_id);
CREATE INDEX idx_relationships_user_id ON relationships(user_id);
CREATE INDEX idx_relationships_chars ON relationships(character1_id, character2_id);

-- إدراج بيانات تجريبية (اختياري)
INSERT INTO users (username, email, password_hash) VALUES
('demo_user', 'demo@narreyes.com', 'scrypt:32768:8:1$salt$hash');

-- رسالة نجاح
SELECT 'Database created successfully!' AS message;
