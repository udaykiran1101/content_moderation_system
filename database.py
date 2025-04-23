import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('moderation.db')
    c = conn.cursor()
    
    # Create flagged content table
    c.execute('''CREATE TABLE IF NOT EXISTS flagged_content
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT NOT NULL,
                  date_flagged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  confidence_score REAL,
                  status TEXT DEFAULT 'pending',
                  admin_notes TEXT,
                  admin_action TEXT,
                  action_date TIMESTAMP)''')
    
    # Create admin users table
    c.execute('''CREATE TABLE IF NOT EXISTS admin_users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL)''')
    
    # Create feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content_id INTEGER NOT NULL,
                  user_feedback TEXT NOT NULL,
                  feedback_text TEXT,
                  date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (content_id) REFERENCES flagged_content(id))''')
    
    # Verify tables exist
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    print("Debug - Existing tables:", tables)
    
    conn.commit()
    conn.close()

def add_flagged_content(content, confidence_score, status='pending'):
    try:
        conn = sqlite3.connect('moderation.db')
        c = conn.cursor()
        
        print(f"Debug - Adding flagged content: {content[:50]}...")  # Log first 50 chars
        
        c.execute('''INSERT INTO flagged_content (content, confidence_score, status) 
                    VALUES (?, ?, ?)''',
                 (content, confidence_score, status))
        
        # Get the inserted content_id
        content_id = c.lastrowid
        print(f"Debug - Added content with ID: {content_id}")
        
        conn.commit()
        return content_id
    except Exception as e:
        print(f"Error in add_flagged_content: {str(e)}")
        return None
    finally:
        conn.close()

def get_flagged_content(status=None, search_term=None):
    conn = sqlite3.connect('moderation.db')
    c = conn.cursor()
    
    query = 'SELECT * FROM flagged_content'
    params = []
    conditions = []
    
    if status and status != 'all':
        conditions.append('status = ?')
        params.append(status)
    
    if search_term:
        conditions.append('content LIKE ?')
        params.append(f'%{search_term}%')
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY date_flagged DESC'
    c.execute(query, params)
    results = c.fetchall()
    
    conn.close()
    return results

def update_content_status(content_id, status, admin_notes=None):
    conn = sqlite3.connect('moderation.db')
    c = conn.cursor()
    
    c.execute('''UPDATE flagged_content 
                 SET status = ?, admin_notes = ?, action_date = CURRENT_TIMESTAMP
                 WHERE id = ?''',
              (status, admin_notes, content_id))
    
    conn.commit()
    conn.close()

def add_admin_user(username, password_hash):
    conn = sqlite3.connect('moderation.db')
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

def verify_admin(username, password_hash):
    conn = sqlite3.connect('moderation.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM admin_users WHERE username = ? AND password_hash = ?',
              (username, password_hash))
    result = c.fetchone()
    
    conn.close()
    return result is not None

def add_feedback(content_id, feedback_type, feedback_text=None):
    try:
        conn = sqlite3.connect('moderation.db')
        c = conn.cursor()
        
        print(f"Debug - Adding feedback: content_id={content_id}, type={feedback_type}, text={feedback_text}")
        
        # Verify content_id exists
        c.execute("SELECT id FROM flagged_content WHERE id = ?", (content_id,))
        if not c.fetchone():
            print(f"Error: Content ID {content_id} does not exist")
            return False
            
        c.execute('''INSERT INTO feedback (content_id, user_feedback, feedback_text) 
                    VALUES (?, ?, ?)''',
                 (content_id, feedback_type, feedback_text))
        
        conn.commit()
        print("Debug - Feedback added successfully")
        return True
    except Exception as e:
        print(f"Error in add_feedback: {str(e)}")
        return False
    finally:
        conn.close()

def get_feedback(content_id=None):
    conn = sqlite3.connect('moderation.db')
    c = conn.cursor()
    
    if content_id:
        c.execute('''SELECT * FROM feedback 
                    WHERE content_id = ? 
                    ORDER BY date_submitted DESC''', (content_id,))
    else:
        c.execute('''SELECT * FROM feedback 
                    ORDER BY date_submitted DESC''')
    
    results = c.fetchall()
    conn.close()
    return results

def get_content_with_feedback(status=None):
    conn = sqlite3.connect('moderation.db')
    c = conn.cursor()
    
    query = '''SELECT fc.*, 
                      COUNT(f.id) as feedback_count,
                      GROUP_CONCAT(f.user_feedback) as feedback_types
               FROM flagged_content fc
               LEFT JOIN feedback f ON fc.id = f.content_id'''
    
    params = []
    if status and status != 'all':
        query += ' WHERE fc.status = ?'
        params.append(status)
    
    query += ''' GROUP BY fc.id
                 ORDER BY fc.date_flagged DESC'''
    
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results 
