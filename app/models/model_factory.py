from app.models.content_model import ContentModel
from app.models.feedback_model import FeedbackModel
from app.models.admin_model import AdminModel

class ModelFactory:
    @staticmethod
    def create_model(model_type):
        if model_type == 'content':
            return ContentModel()
        elif model_type == 'feedback':
            return FeedbackModel()
        elif model_type == 'admin':
            return AdminModel()
        else:
            raise ValueError(f"Unknown model type: {model_type}") 