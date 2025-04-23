from flask import Flask
from app.controllers.content_controller import ContentController
from app.controllers.admin_controller import AdminController
from app.models.admin_model import AdminModel

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key'  # Change this to a secure secret key
    
    # Initialize controllers
    content_controller = ContentController()
    admin_controller = AdminController()
    
    # Initialize admin user if not exists
    admin_model = AdminModel()
    if not admin_model.verify_admin('admin', 'admin'):  # Default credentials
        admin_model.add_admin('admin', 'admin')
    
    # Routes
    @app.route('/')
    def index():
        return content_controller.predict_content()
    
    @app.route('/predict', methods=['POST'])
    def predict():
        return content_controller.predict_content()
    
    @app.route('/feedback', methods=['POST'])
    def feedback():
        return content_controller.submit_feedback()
    
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        return admin_controller.login()
    
    @app.route('/admin')
    def admin_panel():
        return admin_controller.admin_panel()
    
    @app.route('/admin/update_status', methods=['POST'])
    def update_status():
        return admin_controller.update_status()
    
    @app.route('/admin/feedback/<int:content_id>')
    def get_feedback(content_id):
        return admin_controller.get_feedback(content_id)
    
    return app 