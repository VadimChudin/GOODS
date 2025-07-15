from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class UploadFileForm(forms.Form):
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label='Выберите файлы',
        help_text='Поддерживаемые форматы: PNG, JPG, JPEG, GIF, BMP, TIFF'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Загрузить файлы'))


class DeleteDocForm(forms.Form):
    doc_ids_str = forms.CharField(
        label='ID документов',
        help_text='Введите ID документов через запятую',
        widget=forms.TextInput(attrs={'placeholder': '1, 2, 3'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Удалить документы', css_class='btn btn-danger'))

    def clean_doc_ids_str(self):
        doc_ids_str = self.cleaned_data['doc_ids_str']
        try:
            doc_ids = [int(id.strip()) for id in doc_ids_str.split(',')]
            return doc_ids
        except ValueError:
            raise forms.ValidationError('Введите корректные ID документов через запятую')


class AnalyzeDocForm(forms.Form):
    doc_id = forms.IntegerField(
        label='ID документа',
        help_text='Введите ID документа для анализа',
        widget=forms.NumberInput(attrs={'placeholder': '1'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Проанализировать'))


class GetTextForm(forms.Form):
    doc_id = forms.IntegerField(
        label='ID документа',
        help_text='Введите ID документа для получения текста',
        widget=forms.NumberInput(attrs={'placeholder': '1'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Получить текст'))


class CartForm(forms.Form):
    doc_id = forms.IntegerField(
        label='ID документа',
        help_text='Введите ID документа для добавления в корзину',
        widget=forms.NumberInput(attrs={'placeholder': '1'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Добавить в корзину'))
