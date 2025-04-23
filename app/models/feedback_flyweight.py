class FeedbackType:
    def __init__(self, type_name, badge_class):
        self.type_name = type_name
        self.badge_class = badge_class

class FeedbackFlyweightFactory:
    _feedback_types = {}

    @classmethod
    def get_feedback_type(cls, type_name):
        if type_name not in cls._feedback_types:
            badge_class = 'bg-success' if type_name == 'agree' else 'bg-danger'
            cls._feedback_types[type_name] = FeedbackType(type_name, badge_class)
        return cls._feedback_types[type_name]

    @classmethod
    def get_total_types(cls):
        return len(cls._feedback_types) 