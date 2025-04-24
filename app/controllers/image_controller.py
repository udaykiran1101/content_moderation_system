from flask import render_template, request, redirect, url_for
from app.models.image_model import ImageModel
from app.models.feedback_model import FeedbackModel

class ImageController:
    def __init__(self):
        self.image_model = ImageModel()
        self.feedback_model = FeedbackModel()

    def predict_image(self):
        if 'image' not in request.files:
            return render_template('index.html', prediction_text='No image provided.')
            
        image_file = request.files['image']
        if not image_file or image_file.filename == '':
            return render_template('index.html', prediction_text='No image selected.')

        try:
            # Save the image
            image_path = self.image_model.save_image(image_file)
            if not image_path:
                raise Exception("Failed to save image")

            # Predict content
            label, confidence = self.image_model.predict_image(image_path)
            if label is None or confidence is None:
                raise Exception("Failed to analyze image")
            
            # Store image in the database
            status = 'inappropriate' if label == 1 else 'safe'
            image_id = self.image_model.add_image(image_path, float(confidence))
            
            if not image_id:
                raise Exception("Failed to store image in database")

            if label == 0:
                result = f"✅ Safe image ({confidence:.2f} confidence)"
                is_inappropriate = False
            else:
                result = f"⚠️ Inappropriate image detected! ({confidence:.2f} confidence)"
                is_inappropriate = True

            return render_template('index.html', 
                                 prediction_text=result, 
                                 image_id=image_id,
                                 image_path=image_path,
                                 is_inappropriate=is_inappropriate)

        except Exception as e:
            return render_template('index.html', prediction_text=f'Error: {str(e)}')

    def submit_feedback(self):
        try:
            image_id = request.form.get('image_id')
            feedback_type = request.form.get('feedback_type')
            feedback_text = request.form.get('feedback_text')
            
            if not image_id or not feedback_type:
                return redirect(url_for('index'))
                
            self.feedback_model.add_feedback(image_id, feedback_type, feedback_text)
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error in submit_feedback: {str(e)}")
            return redirect(url_for('index')) 