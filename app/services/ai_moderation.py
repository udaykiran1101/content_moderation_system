import requests

class AIModerationService:
    @staticmethod
    def moderate_text(text):
        # Simple keyword-based moderation
        banned_words = ["badword1", "badword2"]
        return any(word in text.lower() for word in banned_words)

    @staticmethod
    def moderate_image(image_url):
        # Example: Use Google Vision API
        response = requests.post("https://some-image-moderation-api.com", json={"image_url": image_url})
        return response.json().get("is_inappropriate", False)
