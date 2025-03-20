class Content:
    def __init__(self, content_id, user_id, content_type, text=None, image_url=None):
        self.content_id = content_id
        self.user_id = user_id
        self.content_type = content_type
        self.text = text
        self.image_url = image_url
        self.status = "Pending"

    def update_status(self, new_status):
        self.status = new_status
