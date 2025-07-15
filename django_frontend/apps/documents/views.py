import os
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Docs, UsersToDocs, Price, Cart
from .forms import UploadFileForm, DeleteDocForm, AnalyzeDocForm, GetTextForm, CartForm
from .services import FastAPIService


def home(request):
    """Главная страница с документами"""
    docs = Docs.objects.all().order_by('-uploaded_at')
    return render(request, 'documents/home.html', {'docs': docs})


@login_required
def upload_file(request):
    """Страница загрузки файла"""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            uploaded_files = []

            for file in files:
                # Проверка типа файла
                if not file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                    messages.error(request, f'Неподдерживаемый формат файла: {file.name}')
                    continue

                # Сохранение файла
                filename = default_storage.save(f'documents/{file.name}', file)
                file_path = os.path.join(settings.MEDIA_ROOT, filename)

                # Получение размера файла в КБ
                file_size = os.path.getsize(file_path) / 1024

                # Отправка в FastAPI
                try:
                    fastapi_service = FastAPIService()
                    with open(file_path, 'rb') as f:
                        response = fastapi_service.upload_document(f, file.name)

                    if response.get('doc_id'):
                        # Создание записи в БД
                        doc = Docs.objects.create(
                            file_path=filename,
                            size=file_size
                        )

                        # Связь с пользователем
                        UsersToDocs.objects.create(
                            username=request.user.username,
                            docs=doc
                        )

                        uploaded_files.append(file.name)
                        messages.success(request, f'Файл {file.name} успешно загружен')
                    else:
                        messages.error(request, f'Ошибка загрузки файла {file.name} в FastAPI')

                except Exception as e:
                    messages.error(request, f'Ошибка при загрузке файла {file.name}: {str(e)}')

            if uploaded_files:
                return redirect('home')
    else:
        form = UploadFileForm()

    return render(request, 'documents/upload_file.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Moderators').exists())
def delete_document(request):
    """Удаление документа (только для модераторов/админов)"""
    if request.method == 'POST':
        form = DeleteDocForm(request.POST)
        if form.is_valid():
            doc_ids = form.cleaned_data['doc_ids']

            for doc_id in doc_ids:
                try:
                    doc = Docs.objects.get(id=doc_id)

                    # Удаление из FastAPI
                    fastapi_service = FastAPIService()
                    response = fastapi_service.delete_document(doc_id)

                    # Удаление файла с диска
                    file_path = os.path.join(settings.MEDIA_ROOT, doc.file_path)
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    # Удаление из БД
                    doc.delete()

                    messages.success(request, f'Документ {doc_id} успешно удален')

                except Docs.DoesNotExist:
                    messages.error(request, f'Документ с ID {doc_id} не найден')
                except Exception as e:
                    messages.error(request, f'Ошибка при удалении документа {doc_id}: {str(e)}')

            return redirect('delete_document')
    else:
        form = DeleteDocForm()

    return render(request, 'documents/delete_document.html', {'form': form})


@login_required
def analyze_document(request):
    """Анализ документа"""
    result = None
    if request.method == 'POST':
        form = AnalyzeDocForm(request.POST)
        if form.is_valid():
            doc_id = form.cleaned_data['doc_id']

            try:
                doc = Docs.objects.get(id=doc_id)

                # Отправка на анализ в FastAPI
                fastapi_service = FastAPIService()
                response = fastapi_service.analyze_document(doc_id)

                result = {
                    'success': True,
                    'message': response.get('detail', 'Анализ запущен'),
                    'doc': doc
                }

            except Docs.DoesNotExist:
                result = {
                    'success': False,
                    'message': f'Документ с ID {doc_id} не найден'
                }
            except Exception as e:
                result = {
                    'success': False,
                    'message': f'Ошибка при анализе документа: {str(e)}'
                }
    else:
        form = AnalyzeDocForm()

    return render(request, 'documents/analyze_document.html', {
        'form': form,
        'result': result
    })


@login_required
def get_text(request):
    """Получение текста документа"""
    result = None
    if request.method == 'POST':
        form = GetTextForm(request.POST)
        if form.is_valid():
            doc_id = form.cleaned_data['doc_id']

            try:
                doc = Docs.objects.get(id=doc_id)

                # Получение текста из FastAPI
                fastapi_service = FastAPIService()
                response = fastapi_service.get_text(doc_id)

                result = {
                    'success': True,
                    'text': response.get('text', 'Текст не найден'),
                    'doc': doc
                }

            except Docs.DoesNotExist:
                result = {
                    'success': False,
                    'message': f'Документ с ID {doc_id} не найден'
                }
            except Exception as e:
                result = {
                    'success': False,
                    'message': f'Ошибка при получении текста: {str(e)}'
                }
    else:
        form = GetTextForm()

    return render(request, 'documents/get_text.html', {
        'form': form,
        'result': result
    })


@login_required
def add_to_cart(request):
    """Добавление документа в корзину"""
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            doc_id = form.cleaned_data['doc_id']

            try:
                doc = Docs.objects.get(id=doc_id)

                # Проверка, нет ли уже в корзине
                cart_item, created = Cart.objects.get_or_create(
                    user=request.user,
                    docs=doc,
                    defaults={'order_price': 0, 'payment': False}
                )

                if created:
                    # Расчет цены
                    try:
                        price = Price.objects.get(file_type=doc.file_extension)
                        cart_item.order_price = doc.size * price.price
                        cart_item.save()

                        messages.success(request,
                                         f'Документ добавлен в корзину. Цена: {cart_item.order_price:.2f} руб.')
                    except Price.DoesNotExist:
                        messages.error(request, f'Цена для типа файла {doc.file_extension} не установлена')
                else:
                    messages.info(request, 'Документ уже есть в корзине')

            except Docs.DoesNotExist:
                messages.error(request, f'Документ с ID {doc_id} не найден')
            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')

            return redirect('add_to_cart')
    else:
        form = CartForm()

    cart_items = Cart.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'documents/add_to_cart.html', {
        'form': form,
        'cart_items': cart_items
    })


@login_required
def pay_order(request, cart_id):
    """Оплата заказа"""
    try:
        cart_item = Cart.objects.get(id=cart_id, user=request.user)
        cart_item.payment = True
        cart_item.save()

        messages.success(request, 'Заказ успешно оплачен!')
        return redirect('payment_success', cart_id=cart_id)

    except Cart.DoesNotExist:
        messages.error(request, 'Заказ не найден')
        return redirect('add_to_cart')


@login_required
def payment_success(request, cart_id):
    """Страница успешной оплаты"""
    try:
        cart_item = Cart.objects.get(id=cart_id, user=request.user, payment=True)

        # Получение результата анализа
        fastapi_service = FastAPIService()
        try:
            text_result = fastapi_service.get_text(cart_item.docs.id)
            analysis_text = text_result.get('text', 'Анализ еще не завершен')
        except:
            analysis_text = 'Анализ еще не завершен'

        return render(request, 'documents/payment_success.html', {
            'cart_item': cart_item,
            'analysis_text': analysis_text
        })

    except Cart.DoesNotExist:
        messages.error(request, 'Заказ не найден или не оплачен')
        return redirect('add_to_cart')