import sqlite3
from datetime import datetime
from predict import predict_text

class ContentModel:
    def __init__(self):
        self.db_name = 'moderation.db'
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
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
        
        conn.commit()
        conn.close()

    def add_content(self, content, confidence_score, status='pending'):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            c.execute('''INSERT INTO flagged_content (content, confidence_score, status) 
                        VALUES (?, ?, ?)''',
                     (content, confidence_score, status))
            
            content_id = c.lastrowid
            conn.commit()
            return content_id
        except Exception as e:
            print(f"Error in add_content: {str(e)}")
            return None
        finally:
            conn.close()

    def get_content(self, status=None, search_term=None):
        conn = sqlite3.connect(self.db_name)
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

    def update_content_status(self, content_id, status, admin_notes=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''UPDATE flagged_content 
                     SET status = ?, admin_notes = ?, action_date = CURRENT_TIMESTAMP
                     WHERE id = ?''',
                  (status, admin_notes, content_id))
        
        conn.commit()
        conn.close()

    def predict_content(self, text):
        try:
            label, confidence = predict_text(text)
            return label, confidence
        except Exception as e:
            print(f"Error in predict_content: {str(e)}")
            return None, None 