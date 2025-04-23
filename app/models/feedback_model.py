import sqlite3
from datetime import datetime

class FeedbackModel:
    def __init__(self):
        self.db_name = 'moderation.db'
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Create feedback table
        c.execute('''CREATE TABLE IF NOT EXISTS feedback
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      content_id INTEGER NOT NULL,
                      user_feedback TEXT NOT NULL,
                      feedback_text TEXT,
                      date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (content_id) REFERENCES flagged_content(id))''')
        
        conn.commit()
        conn.close()

    def add_feedback(self, content_id, feedback_type, feedback_text=None):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Verify content_id exists
            c.execute("SELECT id FROM flagged_content WHERE id = ?", (content_id,))
            if not c.fetchone():
                print(f"Error: Content ID {content_id} does not exist")
                return False
                
            c.execute('''INSERT INTO feedback (content_id, user_feedback, feedback_text) 
                        VALUES (?, ?, ?)''',
                     (content_id, feedback_type, feedback_text))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error in add_feedback: {str(e)}")
            return False
        finally:
            conn.close()

    def get_feedback(self, content_id=None):
        conn = sqlite3.connect(self.db_name)
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

    def get_content_with_feedback(self, status=None):
        conn = sqlite3.connect(self.db_name)
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