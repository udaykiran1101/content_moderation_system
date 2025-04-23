import numpy as np
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import database
import hashlib
from functools import wraps
from predict import predict_text
import sqlite3

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize database
database.init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if database.verify_admin(username, password_hash):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

# Admin panel route
@app.route('/admin')
@login_required
def admin_panel():
    status = request.args.get('status', 'all')
    search = request.args.get('search')
    content = database.get_content_with_feedback(status)
    return render_template('admin.html', content=content)

# API endpoint to update content status
@app.route('/admin/update_status', methods=['POST'])
@login_required
def update_status():
    content_id = request.form.get('content_id')
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    database.update_content_status(content_id, status, notes)
    return jsonify({'success': True})

# Feedback route
@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        content_id = request.form.get('content_id')
        feedback_type = request.form.get('feedback_type')
        feedback_text = request.form.get('feedback_text')
        
        print(f"Debug - Submitting feedback: content_id={content_id}, type={feedback_type}, text={feedback_text}")
        
        if not content_id or not feedback_type:
            print("Error: Missing required fields")
            return redirect(url_for('home'))
            
        database.add_feedback(content_id, feedback_type, feedback_text)
        print("Debug - Feedback successfully added to database")
        
        return redirect(url_for('home'))
    except Exception as e:
        print(f"Error in submit_feedback: {str(e)}")
        return redirect(url_for('home'))

# Route to handle predictions
@app.route('/predict', methods=['POST'])
def predict():
    text_content = request.form.get('textContent')
    if not text_content:
        return render_template('index.html', prediction_text='No text provided.')

    try:
        label, confidence = predict_text(text_content)
        
        # Store content in the database and get the content_id
        status = 'toxic' if label == 1 else 'safe'
        content_id = database.add_flagged_content(text_content, float(confidence))
        
        if not content_id:
            raise Exception("Failed to store content in database")

        if label == 0:
            result = f"✅ Safe comment ({confidence:.2f} confidence)"
            is_inappropriate = False
        else:
            result = f"⚠️ Toxic comment detected! ({confidence:.2f} confidence)"
            is_inappropriate = True

        return render_template('index.html', 
                             prediction_text=result, 
                             content_id=content_id,
                             is_inappropriate=is_inappropriate)

    except Exception as e:
        return render_template('index.html', prediction_text=f'Error: {str(e)}')

# Route to serve the home page
@app.route('/')
def home():
    return render_template('index.html', prediction_text='')

@app.route('/admin/get_feedback/<int:content_id>')
@login_required
def get_feedback(content_id):
    try:
        feedback = database.get_feedback(content_id)
        print(f"Debug - Raw feedback data for content_id {content_id}: {feedback}")
        
        feedback_list = []
        for f in feedback:
            print(f"Debug - Processing feedback item: {f}")
            feedback_list.append({
                'user_feedback': f[2],
                'feedback_text': f[3],
                'date_submitted': f[4]
            })
        
        print(f"Debug - Processed feedback list: {feedback_list}")
        return jsonify({
            'success': True,
            'feedback': feedback_list
        })
    except Exception as e:
        print(f"Error in get_feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/debug/feedback')
@login_required
def debug_feedback():
    conn = sqlite3.connect('moderation.db')
    c = conn.cursor()
    
    # Get all feedback
    c.execute('''SELECT f.*, fc.content 
                FROM feedback f 
                JOIN flagged_content fc ON f.content_id = fc.id 
                ORDER BY f.date_submitted DESC''')
    feedback = c.fetchall()
    
    # Get all flagged content
    c.execute('SELECT * FROM flagged_content ORDER BY date_flagged DESC')
    content = c.fetchall()
    
    conn.close()
    
    return render_template('debug_feedback.html', 
                         feedback=feedback,
                         content=content)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
