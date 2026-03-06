import json
from json import JSONDecodeError

import requests
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from announcement.models import Announcement, Category


def _call_openrouter(messages, temperature=0.4, max_tokens=400):
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    model = settings.OPENROUTER_MODEL
    if not model:
        raise RuntimeError("OPENROUTER_MODEL is not configured.")

    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    if settings.OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
    if settings.OPENROUTER_APP_NAME:
        headers["X-Title"] = settings.OPENROUTER_APP_NAME

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"OpenRouter response missing choices: {data}")

    message = choices[0].get("message", {}) or {}
    text = message.get("content") or message.get("reasoning")
    if not text:
        raise RuntimeError(f"OpenRouter response did not include text. Raw: {data}")

    return str(text).strip()


def _extract_json(text):
    try:
        return json.loads(text)
    except JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start:end + 1])


def _build_category_filter(slugs):
    if not slugs:
        return Q()

    categories = Category.objects.filter(slug__in=slugs)
    parent_ids = [c.id for c in categories if c.parent_id is None]
    child_ids = [c.id for c in categories if c.parent_id is not None]
    category_filter = Q()

    if parent_ids:
        parent_filter = Category.objects.filter(parent_id__in=parent_ids)
        category_filter |= Q(category__in=Category.objects.filter(Q(id__in=parent_ids) | Q(id__in=parent_filter)))

    if child_ids:
        category_filter |= Q(category_id__in=child_ids)

    return category_filter


def _has_any_filter(filters):
    """Return True when *filters* contain at least one meaningful criterion."""
    if not filters:
        return False
    if filters.get("category_slugs"):
        return True
    if filters.get("keywords"):
        return True
    if filters.get("budget_min") is not None or filters.get("budget_max") is not None:
        return True
    if filters.get("condition") in {"new", "used"}:
        return True
    if filters.get("is_negotiable") is True:
        return True
    if filters.get("location"):
        return True
    return False


def _search_announcements(filters):
    qs = Announcement.objects.filter(is_active=True)

    category_slugs = filters.get("category_slugs") or []
    qs = qs.filter(_build_category_filter(category_slugs))

    min_price = filters.get("budget_min")
    max_price = filters.get("budget_max")
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)

    condition = filters.get("condition")
    if condition in {"new", "used"}:
        qs = qs.filter(condition=condition)

    if filters.get("is_negotiable") is True:
        qs = qs.filter(is_negotiable=True)

    location = filters.get("location")
    if location:
        qs = qs.filter(address__icontains=location)

    keywords = [kw for kw in (filters.get("keywords") or []) if kw]
    if keywords:
        keyword_q = Q()
        for kw in keywords:
            keyword_q |= Q(title__icontains=kw) | Q(description__icontains=kw)
        qs = qs.filter(keyword_q)

    return qs.order_by("-created_at")


def _serialize_announcement(request, announcement):
    image = announcement.get_main_image()
    return {
        "id": announcement.id,
        "title": announcement.title,
        "price": str(announcement.price) if announcement.price is not None else None,
        "url": request.build_absolute_uri(
            reverse("announcement:detail", args=[announcement.id])
        ),
        "image": request.build_absolute_uri(image.url) if image else None,
    }


_SYSTEM_PROMPT_TEMPLATE = (
    "Ти — AI-помічник маркетплейсу Amarket. Твоє завдання — допомогти "
    "користувачу знайти потрібний товар. Відповідай ВИКЛЮЧНО валідним JSON "
    "без будь-яких пояснень, коментарів чи markdown.\n\n"
    "Формат відповіді:\n"
    "{{\n"
    '  "should_search": true | false,\n'
    '  "reply": "текст відповіді українською",\n'
    '  "questions": ["уточнюючі питання, якщо потрібно"],\n'
    '  "filters": {{\n'
    '    "category_slugs": [],\n'
    '    "keywords": [],\n'
    '    "budget_min": null,\n'
    '    "budget_max": null,\n'
    '    "condition": null,\n'
    '    "is_negotiable": null,\n'
    '    "location": null\n'
    "  }}\n"
    "}}\n\n"
    "ПРАВИЛА:\n"
    '1. "should_search" — встанови TRUE лише коли у тебе є ДОСТАТНЬО інформації '
    "для конкретного пошуку (є категорія, ключові слова або ціновий діапазон). "
    "Якщо користувач вітається, дякує, ставить загальне питання або ще не дав "
    "достатньо деталей — встанови FALSE.\n"
    '2. "questions" — задавай уточнюючі питання коли потрібно більше деталей '
    "(бюджет, стан, категорія тощо). НЕ шукай коли питаєш.\n"
    '3. "filters" — заповнюй ТІЛЬКИ ті поля, які чітко зрозумілі з контексту. '
    "НЕ вигадуй фільтри.\n"
    '4. "reply" — відповідай дружньо та стисло українською.\n'
    "5. Використовуй тільки наявні slug категорій.\n\n"
    "Приклади:\n"
    'Користувач: "Привіт"\n'
    '{{"should_search": false, "reply": "Привіт! Я ваш AI-помічник. Що шукаєте?", '
    '"questions": [], "filters": {{}}}}\n\n'
    'Користувач: "Хочу подарунок батькові"\n'
    '{{"should_search": false, "reply": "Гарна ідея! Допоможу з вибором.", '
    '"questions": ["Який бюджет?", "Які у нього інтереси?"], "filters": {{}}}}\n\n'
    'Користувач: "Ноутбук до 15000 грн"\n'
    '{{"should_search": true, "reply": "Ось ноутбуки до 15000 грн:", '
    '"questions": [], "filters": {{"category_slugs": ["noutbuky"], '
    '"keywords": ["ноутбук"], "budget_max": 15000}}}}\n\n'
    "Категорії: {category_hint}\n"
)


@require_POST
def assistant_message(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    categories = list(Category.objects.values("name", "slug"))
    category_hint = ", ".join(f"{c['name']} ({c['slug']})" for c in categories[:120])

    history = request.session.get("assistant_history", [])
    history = history[-6:]

    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(category_hint=category_hint)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        raw = _call_openrouter(messages)
        parsed = _extract_json(raw)
    except Exception as exc:
        return JsonResponse({"error": "AI service request failed.", "details": str(exc)}, status=502)

    reply = parsed.get("reply") or "Чим можу допомогти?"
    questions = parsed.get("questions") or []
    filters = parsed.get("filters") or {}
    should_search = parsed.get("should_search", False)

    items = []
    total = 0

    if should_search and _has_any_filter(filters):
        qs = _search_announcements(filters)
        items = [_serialize_announcement(request, a) for a in qs[:6]]
        total = qs.count()

        if total == 0:
            reply = "На жаль, зараз на сайті немає оголошень за таким запитом."
            questions = []

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    request.session["assistant_history"] = history[-10:]
    request.session.modified = True

    return JsonResponse({
        "reply": reply,
        "questions": questions,
        "filters": filters,
        "items": items,
        "total": total,
    })
