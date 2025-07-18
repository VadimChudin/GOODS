
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required   # ← правильный импорт
from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import Docs, Price, Cart
from .services import FastAPIService
import requests

def calculate_price(file_type, size_kb):
    """Цена = размер_в_КБ * цена_за_КБ"""
    price_obj = Price.objects.filter(file_type=file_type.lower()).first()
    return price_obj.price * size_kb if price_obj else 0.0

@login_required
def add_to_cart(request, doc_id):
    doc = get_object_or_404(Docs, id=doc_id)
    price = calculate_price('jpg', doc.size)  # или определите тип файла
    Cart.objects.get_or_create(
        user=request.user,
        docs=doc,
        defaults={'order_price': price}
    )
    return redirect('cart')

@login_required
def pay_cart(request):
    Cart.objects.filter(user=request.user, payment=False).update(payment=True)
    return render(request, 'pay_success.html')


@login_required
def cart(request):
    items = Cart.objects.filter(user=request.user, payment=False)
    total = sum(item.order_price for item in items)
    return render(request, 'cart.html', {'items': items, 'total': total})


def docs_list(request):
    docs = Docs.objects.all().order_by('-id')
    return render(request, 'docs_list.html', {'docs': docs})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('docs_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)

        file_full_path = fs.path(filename)
        try:
            with open(file_full_path, 'rb') as f:
                files = {'file': (uploaded_file.name, f, uploaded_file.content_type)}
                response = requests.post(
                    f"{settings.FASTAPI_URL}/upload_doc",
                    files=files,
                    timeout=30
                )
            if response.status_code == 200:
                fastapi_doc_id = response.json()['doc_id']
                Docs.objects.create(
                    file_path=fs.url(filename),
                    size=uploaded_file.size / 1024,
                    fastapi_id=fastapi_doc_id
                )
            else:
                raise ValueError(response.text)
        except Exception as e:
            fs.delete(filename)
            return render(request, 'error.html', {'error': str(e)})

    return redirect('docs_list')


@login_required
def analyze_document(request, doc_id):
    doc = get_object_or_404(Docs, id=doc_id)
    FastAPIService.analyze_document(doc.fastapi_id)
    text_result = FastAPIService.get_text(doc.fastapi_id)
    return render(request, 'analysis_result.html', {
        'doc': doc,
        'text': text_result.get('text', ''),
        'error': text_result.get('error')
    })


@login_required
def delete_document(request, doc_id):
    doc = get_object_or_404(Docs, id=doc_id)
    FastAPIService.delete_document(doc.fastapi_id)
    doc.delete()
    return redirect('docs_list')


@login_required
def profile(request):
    """Страница профиля"""
    return render(request, 'profile.html')

