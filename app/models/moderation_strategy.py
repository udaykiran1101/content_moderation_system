from abc import ABC, abstractmethod

class ModerationStrategy(ABC):
    @abstractmethod
    def moderate(self, content):
        pass

class ToxicContentStrategy(ModerationStrategy):
    def moderate(self, content):
        # Implement toxic content moderation
        return "toxic", 0.8

class SafeContentStrategy(ModerationStrategy):
    def moderate(self, content):
        # Implement safe content moderation
        return "safe", 0.2

class ContentModerator:
    def __init__(self, strategy: ModerationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ModerationStrategy):
        self._strategy = strategy

    def moderate_content(self, content):
        return self._strategy.moderate(content) 