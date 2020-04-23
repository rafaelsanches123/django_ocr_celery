from celery import current_app
from django.http import JsonResponse
from django.views import View
import json

from .tasks import ocr


class OcrView(View):
    def get(self, request):
        return JsonResponse({'response': 'OCR API WORKS!'})

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        task = ocr.delay(file=data['file'], file_name=data['file_name'])
        context = {}
        context['task_id'] = task.id
        context['task_status'] = task.status
        return JsonResponse(context)


class TaskView(View):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}
        if task.status == 'SUCCESS':
            response_data['results'] = task.get()

        return JsonResponse(response_data)

class HomeView(View):
    def get(self, request):
        return JsonResponse({'response': 'Welcome to OCR API!'})