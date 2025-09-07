from django import forms
from .models import Quote, Source

class QuoteForm(forms.ModelForm):
    source_name = forms.CharField(
        label="Выберите источник",
        required=False,
        help_text="Если источника нет в списке, введите его вручную",
        widget=forms.TextInput(attrs={'list': 'source-list', 'autocomplete': 'off'})
    )

    class Meta:
        model = Quote
        fields = ['text', 'source_name', 'weight']
        labels = {
            'text': 'Текст',
            'weight': 'Вес цитаты',
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if text and Quote.objects.filter(text=text).exists():
            raise forms.ValidationError("Такая цитата уже существует.")
        return text

    def clean_source_name(self):
        source_name = self.cleaned_data.get('source_name')
        if source_name:
            source, _ = Source.objects.get_or_create(name=source_name)
            if Quote.objects.filter(source=source).count() >= 3:
                raise forms.ValidationError(
                    f'Источник "{source_name}" уже содержит 3 цитаты.'
                )
        return source_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        source_name = self.cleaned_data.get('source_name')

        if source_name:
            source, _ = Source.objects.get_or_create(name=source_name)
            instance.source = source

        if commit:
            instance.save()

        return instance
