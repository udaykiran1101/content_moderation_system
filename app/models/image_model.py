import sqlite3
from datetime import datetime
import os
from PIL import Image
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.predict import predict_image

class ImageModel:
    def __init__(self):
        self.db_name = 'moderation.db'
        self.upload_folder = 'static/uploads'
        self.init_db()
        
        # Create uploads directory if it doesn't exist
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Create flagged images table
        c.execute('''CREATE TABLE IF NOT EXISTS flagged_images
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      image_path TEXT NOT NULL,
                      date_flagged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      confidence_score REAL,
                      status TEXT DEFAULT 'pending',
                      admin_notes TEXT,
                      admin_action TEXT,
                      action_date TIMESTAMP)''')
        
        conn.commit()
        conn.close()

    def save_image(self, image_file):
        try:
            # Generate unique filename
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_file.filename}"
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save the image
            image = Image.open(image_file)
            image.save(filepath)
            
            return filepath
        except Exception as e:
            print(f"Error in save_image: {str(e)}")
            return None

    def add_image(self, image_path, confidence_score, status='pending'):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            c.execute('''INSERT INTO flagged_images (image_path, confidence_score, status) 
                        VALUES (?, ?, ?)''',
                     (image_path, confidence_score, status))
            
            image_id = c.lastrowid
            conn.commit()
            return image_id
        except Exception as e:
            print(f"Error in add_image: {str(e)}")
            return None
        finally:
            conn.close()

    def get_images(self, status=None, search_term=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        query = 'SELECT * FROM flagged_images'
        params = []
        conditions = []
        
        if status and status != 'all':
            conditions.append('status = ?')
            params.append(status)
        
        if search_term:
            conditions.append('image_path LIKE ?')
            params.append(f'%{search_term}%')
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY date_flagged DESC'
        c.execute(query, params)
        results = c.fetchall()
        
        conn.close()
        return results

    def update_image_status(self, image_id, status, admin_notes=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''UPDATE flagged_images 
                     SET status = ?, admin_notes = ?, action_date = CURRENT_TIMESTAMP
                     WHERE id = ?''',
                  (status, admin_notes, image_id))
        
        conn.commit()
        conn.close()

    def predict_image(self, image_path):
        try:
            label, confidence = predict_image(image_path)
            return label, confidence
        except Exception as e:
            print(f"Error in predict_image: {str(e)}")
            return None, None 