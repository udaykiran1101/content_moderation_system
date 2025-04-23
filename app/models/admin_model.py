import sqlite3
import hashlib

class AdminModel:
    def __init__(self):
        self.db_name = 'moderation.db'
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Create admin users table
        c.execute('''CREATE TABLE IF NOT EXISTS admin_users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password_hash TEXT NOT NULL)''')
        
        conn.commit()
        conn.close()

    def add_admin(self, username, password_hash):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO admin_users (username, password_hash) VALUES (?, ?)',
                      (username, password_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def verify_admin(self, username, password_hash):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('SELECT id FROM admin_users WHERE username = ? AND password_hash = ?',
                  (username, password_hash))
        result = c.fetchone()
        
        conn.close()
        return result is not None 