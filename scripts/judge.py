"""Best-of-3 generation + judge scoring for social posts.

Two pure-function parsers (variant splitter, score parser) and one selector.
The Gemini calls themselves live in generate_social.py; this module isolates
the format handling so it's testable without network.
"""

import json
import re

GENERATION_PREAMBLE = """Ти си български сатирик. Целта ти: пост който кара читателя ДА СЕ ИЗСМЕЕ ТИХО НА ТЕЛЕФОНА В ОФИСА.
Не общи фрази, а специфични. Ползвай:
- Конкретни институции: НАП, КАТ, БДЖ, ЕОН/ЧЕЗ, общината, "областна"
- Конкретни моменти: "елате утре", "системата не работи", "не съм оторизирана", "този прозорец не работи", "обедна почивка от 10:05 до 17:00"
- Конкретни абсурди: печат върху печат, формуляр в 3 копия, час за след 3 месеца, гише 7
- Конкретни хора: "леля на гише 3", "охранителят който не знае нищо"

Избягвай: "Опа, бюрокрация!", "Браво на администрацията!", общи философски заключения.
Бъди КОНКРЕТЕН. Образът да е виден. Шегата да е остра.

Сега, ето задачата:
{task}

ВЪРНИ 3 ВАРИАНТА разделени с ред "---". Без номерация. Без обяснения. Само трите поста."""

JUDGE_PROMPT = """Ти си строг редактор на сатиричен портал. Имаш 3 варианта на Facebook пост.
Оцени всеки 1-10 по два критерия:
- laugh: реално ли е смешно (1=не, 10=ще се смея на глас)
- share: бих ли го споделил с приятел (1=не, 10=веднага)

Бъди строг. Средното не е 7 — средното е 4.

Варианти:
1. {v1}
2. {v2}
3. {v3}

Върни САМО JSON масив: [{{"laugh":N,"share":N}},{{"laugh":N,"share":N}},{{"laugh":N,"share":N}}]"""

REGEN_NOTE = "\n\nПредишните варианти бяха слаби. Бъди по-конкретен и по-остър."

THRESHOLD = 14


def parse_variants(raw):
    blocks = [b.strip() for b in raw.split("---") if b.strip()]
    cleaned = [re.sub(r"^\s*\d+[\.\)]\s*", "", b) for b in blocks]
    while len(cleaned) < 3 and cleaned:
        cleaned.append(cleaned[-1])
    return cleaned[:3]


def parse_scores(raw):
    fence = re.search(r"```(?:json)?\s*(.*?)```", raw, flags=re.S)
    payload = fence.group(1) if fence else raw
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, list) or len(data) != 3:
        return None
    for entry in data:
        if not isinstance(entry, dict) or "laugh" not in entry or "share" not in entry:
            return None
    return data


def pick_best(variants, scores):
    if not scores:
        return variants[0], 0
    totals = [s["laugh"] + s["share"] for s in scores]
    best_idx = totals.index(max(totals))
    return variants[best_idx], totals[best_idx]
