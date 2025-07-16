from django.shortcuts import render, redirect
from django_app.models import Docs
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from .services import FastAPIService
from django.conf import settings


def docs_list(request):
    """Главная страница со списком документов"""
    docs = Docs.objects.all().order_by('-id')
    return render(request, 'docs_list.html', {
        'docs': docs,
        'fastapi_url': settings.FASTAPI_URL
    })


def upload_file(request):
    """Загрузка файла"""
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

        except Exception as e:
            return render(request, 'error.html', {
                'error': f'Ошибка при загрузке файла: {str(e)}'
            })

    return redirect('docs_list')


def analyze_document(request, doc_id):

    try:
        doc = Docs.objects.get(id=doc_id)

        # Запуск анализа
        analysis_result = FastAPIService.analyze_document(doc_id)

        # Получение результата
        text_result = FastAPIService.get_text(doc_id)

        return render(request, 'analysis_result.html', {
            'doc': doc,
            'status': analysis_result.get('status'),
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
    """Удаление документа"""
    try:
        doc = Docs.objects.get(id=doc_id)

        # Удаление через FastAPI
        if FastAPIService.delete_document(doc_id):
            # Удаление из Django
            doc.delete()
            return redirect('docs_list')
        else:
            raise Exception('Не удалось удалить документ в FastAPI')

    except Docs.DoesNotExist:
        raise Http404("Документ не найден")
    except Exception as e:
        return render(request, 'error.html', {
            'error': f'Ошибка при удалении документа: {str(e)}'
        })