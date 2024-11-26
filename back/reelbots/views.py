from django.shortcuts import render
from rest_framework.decorators import api_view
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import openai
from .models import ChatHistory  # 모델 임포트

# OpenAI API 키 설정
openai.api_key = settings.OPENAI_API_KEY

@api_view(['POST'])
@csrf_exempt
def run_chatbot(request):
    if request.method == "POST":
        try:
            # 클라이언트 요청 데이터 가져오기
            data = json.loads(request.body)
            user_input = data.get("message", "")
            
            if not user_input:
                return JsonResponse({"error": "No message provided"}, status=400)

            # OpenAI API 호출
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # 사용할 모델 이름
                messages=[
                    {"role": "system", "content": "You are a friendly and knowledgeable chatbot designed to assist users on a movie recommendation website. Your primary goals are to provide personalized movie recommendations, answer movie-related questions, and guide users through the website's features. Use a conversational and engaging tone to ensure users feel comfortable interacting with you. When making recommendations, consider genres, user preferences, trending movies, and critically acclaimed titles. Always respond concisely and helpfully. If you don't know the answer, politely let the user know and suggest alternative actions or resources."},
                    {"role": "user", "content": user_input},
                ]
            )
            
            # 응답 데이터 추출
            chatbot_response = response['choices'][0]['message']['content']

            # 데이터베이스에 저장
            ChatHistory.objects.create(user_input=user_input, chatbot_response=chatbot_response)

            return JsonResponse({"response": chatbot_response})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
