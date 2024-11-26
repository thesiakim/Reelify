from django.db import models

# Create your models here.
class ChatHistory(models.Model):
    user_input = models.TextField()  # 유저가 입력한 메시지
    chatbot_response = models.TextField()  # 챗봇의 응답
    timestamp = models.DateTimeField(auto_now_add=True)  # 저장 시간

    def __str__(self):
        return f"User: {self.user_input[:50]} - Chatbot: {self.chatbot_response[:50]}"
