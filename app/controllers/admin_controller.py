from flask import render_template, request, jsonify, session, redirect, url_for
from app.models.admin_model import AdminModel
from app.models.content_model import ContentModel
from app.models.image_model import ImageModel
from app.models.feedback_model import FeedbackModel
import hashlib

class AdminController:
    def __init__(self):
        self.admin_model = AdminModel()
        self.content_model = ContentModel()
        self.image_model = ImageModel()
        self.feedback_model = FeedbackModel()

    def login(self):
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if self.admin_model.verify_admin(username, password_hash):
                session['admin_logged_in'] = True
                return redirect(url_for('admin_panel'))
            return render_template('admin_login.html', error='Invalid credentials')
        return render_template('admin_login.html')

    def admin_panel(self):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
            
        status = request.args.get('status', 'all')
        search = request.args.get('search')
        
        # Get both text and image content
        text_content = self.content_model.get_content(status, search)
        image_content = self.image_model.get_images(status, search)
        
        # Combine and sort content
        all_content = []
        for item in text_content:
            all_content.append({
                'id': item[0],
                'content': item[1],
                'date': item[2],
                'confidence': item[3],
                'status': item[4],
                'type': 'text'
            })
            
        for item in image_content:
            all_content.append({
                'id': item[0],
                'content': item[1],  # This is the image path
                'date': item[2],
                'confidence': item[3],
                'status': item[4],
                'type': 'image'
            })
            
        # Sort by date
        all_content.sort(key=lambda x: x['date'], reverse=True)
        
        return render_template('admin.html', content=all_content, status=status, search=search)

    def update_status(self):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authorized'})
            
        content_id = request.form.get('content_id')
        content_type = request.form.get('content_type')
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        if content_type == 'text':
            self.content_model.update_content_status(content_id, status, notes)
        else:
            self.image_model.update_image_status(content_id, status, notes)
            
        return jsonify({'success': True})

    def get_feedback(self, content_id):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authorized'})
            
        try:
            feedback = self.feedback_model.get_feedback(content_id)
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