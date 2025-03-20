from flask import request, render_template
from models.content import Content
from services.ai_moderation import AIModerationService

class ContentController:
    @staticmethod
    def submit_content():
        text = request.form.get("text")
        image_url = request.form.get("image_url")
        
        # Create content object
        content = Content(content_id=1, user_id=1, content_type="text", text=text)
        
        # Moderate content
        if text and AIModerationService.moderate_text(text):
            content.update_status("Flagged")
        
        if image_url and AIModerationService.moderate_image(image_url):
            content.update_status("Flagged")

        return render_template("results.html", content=content)
