from django.db import models
from django.core.exceptions import ValidationError

class Source(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"


class Quote(models.Model):
    text = models.TextField(unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='quotes')
    weight = models.PositiveIntegerField(default=1)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text if len(self.text) <= 50 else f"{self.text[:50]}..."

    def clean(self):
        if self.source and not self.pk:
            if Quote.objects.filter(source=self.source).count() >= 3:
                raise ValidationError(f'Источник "{self.source.name}" уже содержит 3 цитаты.')

    class Meta:
        ordering = ['-likes']
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"
