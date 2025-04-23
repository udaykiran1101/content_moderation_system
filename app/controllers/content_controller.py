from flask import render_template, request, redirect, url_for
from app.models.content_model import ContentModel
from app.models.feedback_model import FeedbackModel

class ContentController:
    def __init__(self):
        self.content_model = ContentModel()
        self.feedback_model = FeedbackModel()

    def predict_content(self):
        text_content = request.form.get('textContent')
        if not text_content:
            return render_template('index.html', prediction_text='No text provided.')

        try:
            label, confidence = self.content_model.predict_content(text_content)
            
            # Store content in the database
            status = 'toxic' if label == 1 else 'safe'
            content_id = self.content_model.add_content(text_content, float(confidence))
            
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

    def submit_feedback(self):
        try:
            content_id = request.form.get('content_id')
            feedback_type = request.form.get('feedback_type')
            feedback_text = request.form.get('feedback_text')
            
            if not content_id or not feedback_type:
                return redirect(url_for('index'))
                
            self.feedback_model.add_feedback(content_id, feedback_type, feedback_text)
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error in submit_feedback: {str(e)}")
            return redirect(url_for('index')) 