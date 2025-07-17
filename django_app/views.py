from django.shortcuts import render, redirect
from django_app.models import Docs
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from .services import FastAPIService
from django.conf import settings
import requests
import os


def docs_list(request):
    """Главная страница со списком документов"""
    docs = Docs.objects.all().order_by('-id')
    return render(request, 'docs_list.html', {
        'docs': docs,
        'fastapi_url': settings.FASTAPI_URL
    })


def upload_file(request):
    """Загрузка файла с синхронизацией в FastAPI"""
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()

            # Сохранение файла
            filename = fs.save(uploaded_file.name, uploaded_file)

            # Сохранение в БД Django
            doc = Docs(
                file_path=fs.url(filename),
                size=uploaded_file.size / 1024  # Размер в КБ
            )
            doc.save()

            # Загрузка файла в FastAPI
            try:
                file_full_path = fs.path(filename)
                with open(file_full_path, 'rb') as f:
                    files = {'file': (uploaded_file.name, f, uploaded_file.content_type)}
                    response = requests.post(
                        f"{settings.FASTAPI_URL}/upload_doc",
                        files=files,
                        timeout=30
                    )
                    if response.status_code == 200:
                        fastapi_doc_id = response.json().get('doc_id')
                        print(f"Файл загружен в FastAPI с ID: {fastapi_doc_id}")
                    else:
                        print(f"Ошибка загрузки в FastAPI: {response.text}")
            except Exception as e:
                print(f"Ошибка при загрузке в FastAPI: {e}")

        except Exception as e:
            return render(request, 'error.html', {
                'error': f'Ошибка при загрузке файла: {str(e)}'
            })

    return redirect('docs_list')


def analyze_document(request, doc_id):
    """Анализ документа"""
    try:
        doc = Docs.objects.get(id=doc_id)

        # Запуск анализа
        analysis_result = FastAPIService.analyze_document(doc_id)

        # Получение результата
        text_result = FastAPIService.get_text(doc_id)

        return render(request, 'analysis_result.html', {
            'doc': doc,
            'status': analysis_result.get('detail', 'Анализ запущен'),
            'text': text_result.get('text', 'Текст не распознан'),
            'error': text_result.get('error')
        })

    except Docs.DoesNotExist:
        raise Http404("Документ не найден")
    except Exception as e:
        return render(request, 'error.html', {
            'error': f'Ошибка при анализе документа: {str(e)}'
        })


def delete_document(request, doc_id):
    """Удаление документа с синхронизацией"""
    try:
        doc = Docs.objects.get(id=doc_id)

        # Удаление файла из файловой системы
        if doc.file_path:
            try:
                # Получаем полный путь к файлу
                file_path = os.path.join(settings.MEDIA_ROOT, doc.file_path.lstrip('/media/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Файл {file_path} удален из файловой системы")
            except Exception as e:
                print(f"Ошибка при удалении файла: {e}")

        # Попытка удаления через FastAPI (не критично если не удалось)
        try:
            FastAPIService.delete_document(doc_id)
            print(f"Документ {doc_id} удален из FastAPI")
        except Exception as e:
            print(f"Ошибка при удалении из FastAPI: {e}")

        # Удаление из Django БД
        doc.delete()
        print(f"Документ {doc_id} удален из Django БД")

        return redirect('docs_list')

    except Docs.DoesNotExist:
        raise Http404("Документ не найден")
    except Exception as e:
        return render(request, 'error.html', {
            'error': f'Ошибка при удалении документа: {str(e)}'
        })