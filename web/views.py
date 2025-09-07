import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import F
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Quote, Source
from .forms import QuoteForm


def weighted_random_choice(quotes):
    total_weight = sum(q.weight for q in quotes)
    if total_weight == 0:
        return random.choice(quotes)  # или None, если так задумано
    r = random.uniform(0, total_weight)
    upto = 0
    for q in quotes:
        if upto + q.weight >= r:
            return q
        upto += q.weight


def random_quote_view(request):
    quotes = Quote.objects.all()
    if not quotes:
        return render(request, 'web/random_quote.html', {'quote': None})

    quote = weighted_random_choice(quotes)
    Quote.objects.filter(pk=quote.pk).update(views=F('views') + 1)

    return render(request, 'web/random_quote.html', {'quote': quote})


@require_POST
def like_quote_api(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    action = request.POST.get('action')

    if action == 'like':
        Quote.objects.filter(pk=quote.pk).update(likes=F('likes') + 1)
    elif action == 'dislike':
        Quote.objects.filter(pk=quote.pk).update(dislikes=F('dislikes') + 1)
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)

    quote.refresh_from_db()

    return JsonResponse({
        'likes': quote.likes,
        'dislikes': quote.dislikes,
    })


def add_quote_view(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('random_quote'))  # лучше с reverse
    else:
        form = QuoteForm()

    sources = Source.objects.all()
    return render(request, 'web/add_quote.html', {'form': form, 'sources': sources})


def top_quotes_view(request):
    top_quotes = Quote.objects.order_by('-likes')[:10]
    return render(request, 'web/top_quotes.html', {'quotes': top_quotes})


def all_quotes_view(request):
    sources = Source.objects.all()
    quotes = Quote.objects.all()

    current_filters = {
        'source': request.GET.get('source', ''),
        'min_likes': request.GET.get('min_likes', ''),
        'min_weight': request.GET.get('min_weight', ''),
        'sort_by': request.GET.get('sort_by', 'created_at'),
        'direction': request.GET.get('direction', 'desc'),
    }


    return render(request, 'web/all_quotes.html', {
        'sources': sources,
        'quotes': quotes,
        'current_filters': current_filters,
    })


def apply_quote_filters(queryset, params):
    source_id = params.get('source')
    if source_id:
        queryset = queryset.filter(source_id=source_id)

    min_likes = params.get('min_likes')
    if min_likes:
        try:
            queryset = queryset.filter(likes__gte=int(min_likes))
        except ValueError:
            pass

    min_weight = params.get('min_weight')
    if min_weight:
        try:
            queryset = queryset.filter(weight__gte=int(min_weight))
        except ValueError:
            pass

    sort_by = params.get('sort_by', 'created_at')
    direction = params.get('direction', 'desc')
    ordering = f"-{sort_by}" if direction == 'desc' else sort_by
    queryset = queryset.order_by(ordering)

    return queryset


def filter_quotes_ajax(request):
    quotes = apply_quote_filters(Quote.objects.all(), request.GET)
    html = render_to_string('web/quotes_list.html', {'quotes': quotes})
    return JsonResponse({'html': html})
