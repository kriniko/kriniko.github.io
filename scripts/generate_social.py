#!/usr/bin/env python3
"""Generate one Facebook post per run.

Flow:
  1. pick category (round-robin) + template (avoid recent)
  2. Gemini: 3 text variants
  3. Gemini: judge scores -> pick best (regen once if max < THRESHOLD)
  4. Gemini: 1-sentence English scene prompt for visual
  5. dispatch visual by category.visual_type
  6. write social-output.json with {text, image_url}
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import date
from pathlib import Path

from google import genai

from categories import CATEGORIES, pick_category, pick_template
from judge import (
    GENERATION_PREAMBLE,
    JUDGE_PROMPT,
    REGEN_NOTE,
    THRESHOLD,
    parse_scores,
    parse_variants,
    pick_best,
)
import visuals

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]
MAX_API_RETRIES = 3
API_RETRY_DELAY = 30
SOCIAL_HISTORY_FILE = REPO_ROOT / "content" / "social-history.json"
CONTENT_DIR = REPO_ROOT / "content" / "article"
SITE_BASE_URL = "https://gisheto.com"

# Content calendar: 27 rotating post types based on the content plan
# Each has a type, a Bulgarian prompt, and suggested hashtags
POST_TEMPLATES = [
    {
        "type": "current_absurdity",
        "name": "Актуален бюрократичен абсурд",
        "prompt": """Измисли кратък Facebook пост (3-5 изречения) коментиращ актуален бюрократичен абсурд в България.
Започни с провокативен въпрос или удивление. Звучи като истинска новина, но леко преувеличена.
Пример: "Чухте ли последната? Общината въвежда електронна опашка... за която трябва да чакаш на физическа опашка."
Пиши на БЪЛГАРСКИ. Завърши с призив за коментар.""",
        "hashtags": "#БюрокрацияБезКрай #БългарскаРеалност #АдминистративенАбсурд",
    },
    {
        "type": "interactive_poll",
        "name": "Интерактивна анкета",
        "prompt": """Създай Facebook анкета свързана с българската бюрокрация.
Формат:
Въпрос (закачлив)
A) вариант 1
B) вариант 2
C) вариант 3
D) Всичко горепосочено!

Пример: "Кое ви дразни най-много в администрацията?
A) Безкрайните опашки
B) Планините от документи
C) Противоречивата информация
D) Всичко горепосочено!"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Бюрокрация #НароднаМъдрост #Гласувай",
    },
    {
        "type": "historical_bureaucracy",
        "name": "Историческа бюрокрация",
        "prompt": """Напиши кратък Facebook пост (2-4 изречения) свързващ съвременната българска бюрокрация с историческа.
Може да е от Османско време, комунизма, или прехода. Хуморът е в това, че нищо не се е променило.
Пример: "Казват, че историята се повтаря. Особено когато става дума за бюрокрация! Знаехте ли, че още през 1923 г. гражданите се оплаквали от опашките в общината? Звучи ли ви познато?"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#История #БюрокрацияПрезВековете #ВечниПроблеми",
    },
    {
        "type": "educational_satire",
        "name": "Образователна сатира",
        "prompt": """Напиши кратък Facebook пост (3-5 изречения) който "обяснява" сложна административна процедура по сатиричен начин.
Представи се като полезен наръчник, но с абсурдни стъпки.
Пример: "Навигирането през процедурата за смяна на адрес е като опит да решиш кубчето на Рубик с вързани очи. Ето нашия опростен (и леко саркастичен) наръчник!"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#КакДа #БюрократиченНаръчник #Сарказъм",
    },
    {
        "type": "behind_the_scenes",
        "name": "Зад кулисите",
        "prompt": """Напиши кратък Facebook пост (2-3 изречения) от името на "Гише ∞" — сякаш споделяш откъде идва вдъхновението за сатиричните статии.
Тонът е приятелски и леко самоироничен.
Пример: "Чудите ли се откъде черпим вдъхновение? Понякога реалността пише най-добрите вицове! Днешната статия ни беше вдъхновена от реален разговор на гише..."
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#ЗадКулисите #ТворческиПроцес #ГишеБезКрайност",
    },
    {
        "type": "weekend_humor",
        "name": "Уикенд хумор",
        "prompt": """Напиши кратък весел Facebook пост (2-3 изречения) за бягство от бюрокрацията през уикенда.
Лек, позитивен тон с хумористичен обрат.
Пример: "Най-накрая уикенд! Време е да се освободим от безкрайните формуляри и да прегърнем свободата... до понеделник."
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Уикенд #Свобода #БюрокрацияНаПауза",
    },
    {
        "type": "engaging_question",
        "name": "Въпрос за дискусия",
        "prompt": """Напиши Facebook пост с един провокативен въпрос за българската бюрокрация (1-2 изречения + въпрос).
Целта е хората да коментират.
Пример: "Ако можехте моментално да промените едно бюрократично правило, кое щеше да е и защо? Да помечтаем!"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#НеделниРазмисли #Промени #Мечти",
    },
    {
        "type": "meme_text",
        "name": "Мийм текст",
        "prompt": """Напиши КРАТЪК мийм текст (2-4 реда максимум) за българската бюрокрация.
Формат: ситуация → обрат. Максимално кратко и споделяемо.
Примери:
- "Отиваш в общината за 5 минути. Излизаш след 5 часа. С грешен документ."
- "Гише 7: Отворено от 10 до 10:05. Обедна почивка от 10:05 до 17:00."
- "Това чувство, когато най-после стигнеш до гишето... и ти казват, че си на грешното."
Пиши на БЪЛГАРСКИ. Върни САМО текста.""",
        "hashtags": "#Мем #БюрократиченХумор #Живот",
    },
    {
        "type": "satirical_fact",
        "name": "Сатиричен факт",
        "prompt": """Измисли фалшива но правдоподобна статистика за българската бюрокрация. Формат: "Знаехте ли, че..."
Трябва да звучи като истинска статистика, но да е абсурдна.
Добави (Дисклеймър: Може да съдържа следи от сатира).
Примери:
- "Знаехте ли, че са нужни приблизително 3.7 дървета за да се отпечата средният бюрократичен документ?"
- "Знаехте ли, че средностатистическият българин прекарва 47 дни от живота си в чакане пред гишета?"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Сатира #Факти #ЗнаехтеЛи",
    },
    {
        "type": "user_stories",
        "name": "Покана за истории",
        "prompt": """Напиши Facebook пост (2-3 изречения) който приканва хората да споделят техните бюрократични кошмари.
Тонът е съчувствен и хумористичен — "всички сме минали през това".
Пример: "Всеки има поне една. Кой е вашият най-незабравим бюрократичен кошмар? Разкажете в коментарите!"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#МоятаИстория #БюрократиченУжас #Разкажи",
    },
    {
        "type": "bureaucrat_quote",
        "name": "Цитат от бюрократ",
        "prompt": """Измисли ФАЛШИВ цитат от измислен български бюрократ. Трябва да звучи абсолютно автентично.
Формат:
"Цитатът тук" — Име Фамилия, Длъжност

Примери:
"Системата работи перфектно. Просто не е включена." — Инж. Сървъров, Началник ИТ отдел, МВР
"Ние сме отворени за граждани всеки ден. Просто не за тези граждани." — Г-жа Затворкова, Гише 12
Пиши на БЪЛГАРСКИ. Върни САМО цитата.""",
        "hashtags": "#Цитат #Бюрокрация #ИзмисленоНоРеално",
    },
    {
        "type": "personification",
        "name": "Ако бюрокрацията беше човек",
        "prompt": """Напиши кратък Facebook пост (2-3 изречения) описващ бюрокрацията като човек.
Творчески, хумористичен, визуален.
Пример: "Ако бюрокрацията беше човек, щеше да има печат за всеки повод и табела 'Елате утре' завинаги залепена на челото."
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Персонификация #Бюрокрация #ПредставиСи",
    },
    {
        "type": "pro_tip",
        "name": "Саркастичен съвет",
        "prompt": """Напиши кратък саркастичен "съвет" за справяне с бюрокрацията (1-2 изречения).
Формат: "Про-тип: ..."
Пример: "Про-тип за справяне с бюрокрацията: Винаги носи закуски. Чакането е дълго."
Пиши на БЪЛГАРСКИ. Кратко и остро.""",
        "hashtags": "#Съвет #Сарказъм #Оцеляване",
    },
    {
        "type": "comparison",
        "name": "Хумористично сравнение",
        "prompt": """Напиши Facebook пост (2-3 изречения) сравняващ бюрократичен процес с нещо друго абсурдно.
Завърши с "А вашето любимо сравнение?"
Пример: "Опитът да разбереш процедурата е като да пасеш котки, докато жонглираш с горящи факли."
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Сравнение #Абсурд #Бюрокрация",
    },
    {
        "type": "bureaucracy_bingo",
        "name": "Бюрократично бинго",
        "prompt": """Създай бинго карта с 9 типични бюрократични фрази/ситуации (3x3).
Формат:
🟦 БЮРОКРАТИЧНО БИНГО 🟦
[фраза 1] | [фраза 2] | [фраза 3]
[фраза 4] | [фраза 5] | [фраза 6]
[фраза 7] | [фраза 8] | [фраза 9]

Колко можете да отбележите от последното си посещение в администрацията?
Пиши на БЪЛГАРСКИ. Фразите да са кратки (3-5 думи).""",
        "hashtags": "#Бинго #Игра #Бюрокрация",
    },
    {
        "type": "old_article_hook",
        "name": "Закачка за стара статия",
        "prompt": """На базата на тази статия, напиши кратък закачлив Facebook пост (2-3 изречения)
който да привлече хората да я прочетат. Използвай различен ъгъл — въпрос, провокация, или "а вие опитвали ли сте..."
Завърши с {{link}}
Пиши на БЪЛГАРСКИ. Върни САМО текста на поста.""",
    },
    {
        "type": "theme_song",
        "name": "Тематична песен",
        "prompt": """Напиши Facebook пост-въпрос (1-2 изречения):
"Ако бюрокрацията имаше химн/тематична песен, коя щеше да е?"
Добави 2-3 смешни предложения и попитай за техните.
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Музика #Бюрокрация #Въпрос",
    },
    {
        "type": "monthly_reflection",
        "name": "Месечна равносметка",
        "prompt": """Напиши Facebook пост (2-3 изречения) — хумористична равносметка на битката с бюрокрацията.
Тон: оптимистичен въпреки всичко.
Пример: "Още един месец, още един кръг с бюрократичния звяр. Все още сме тук, все още се смеем (предимно). Коя е вашата най-голяма бюрократична победа този месец?"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Размисли #Победа #Бюрокрация",
    },
    {
        "type": "tag_a_friend",
        "name": "Тагни приятел",
        "prompt": """Напиши кратък Facebook пост (2-3 изречения) който завършва с призив "Тагнете приятел, който..."
Ситуацията трябва да е свързана с бюрокрация — нещо, което всеки е преживял.
Примери:
- "Тагнете приятел, който е чакал повече от 3 часа на гише."
- "Тагнете приятел, който все още не си е подал данъчната декларация."
Пиши на БЪЛГАРСКИ. Кратко, споделяемо, забавно.""",
        "hashtags": "#Тагни #Приятел #Бюрокрация #Споделяемо",
    },
    {
        "type": "this_or_that",
        "name": "Това или онова",
        "prompt": """Създай Facebook пост с избор между две бюрократични ситуации — коя е по-лоша?
Формат:
🔴 [ситуация 1]
или
🔵 [ситуация 2]

И двете трябва да са реалистични и болезнено познати.
Пример:
🔴 Да разбереш, че си на грешното гише след 2 часа чакане
или
🔵 Да разбереш, че ти липсва ЕДИН документ и трябва да дойдеш пак утре
Завърши с "Кое бихте избрали? 👇"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#ТоваИлиОнова #Избор #Бюрокрация",
    },
    {
        "type": "finish_the_sentence",
        "name": "Довършете изречението",
        "prompt": """Напиши Facebook пост с незавършено изречение, свързано с бюрокрация, което хората да довършат.
Формат: Довършете изречението: "Когато чуя 'елате утре'..."
Дай 2-3 забавни примерни отговора, после покани хората да споделят.
Пиши на БЪЛГАРСКИ. Кратко и интерактивно.""",
        "hashtags": "#Довършете #Игра #Бюрокрация",
    },
    {
        "type": "weekend_meme",
        "name": "Уикенд мийм",
        "prompt": """Напиши МНОГО КРАТЪК мийм текст (2-3 реда) за уикенда и бюрокрацията.
Тон: леко празничен, облекчен.
Примери:
- "Уикендът е единственото време, когато бюрокрацията не може да те достигне. Освен ако нямаш недовършени документи. Тогава те преследва и насън."
- "Петък, 16:59. Гишето затваря. Понеделник е далеч. Животът е хубав."
Пиши на БЪЛГАРСКИ. Максимално кратко и споделяемо.""",
        "hashtags": "#Уикенд #ТГИФ #СвободаОтГишето",
    },
    {
        "type": "did_you_know_real",
        "name": "Знаехте ли (реален факт)",
        "prompt": """Напиши Facebook пост с РЕАЛЕН интересен факт за българската бюрокрация или администрация.
Може да е: брой на формулярите, работно време, исторически факт, сравнение с друга държава.
Формат: "Знаехте ли, че..." + кратък коментар.
Пример: "Знаехте ли, че България има над 260 различни административни услуги, които изискват лично присъствие? В Естония същите услуги се правят онлайн за 5 минути. Но пък ние имаме по-хубаво време. 😎"
Пиши на БЪЛГАРСКИ. Информативно но леко.""",
        "hashtags": "#ЗнаехтеЛи #Факт #Бюрокрация #България",
    },
    {
        "type": "before_after",
        "name": "Преди и след гишето",
        "prompt": """Напиши кратък Facebook пост в формат "преди/след" посещение на гише.
Формат:
Преди гишето: [описание]
След гишето: [описание]

Хуморът е в контраста — оптимизъм преди, опустошение след.
Пример:
"Преди гишето: пълен с надежда, подредени документи, усмивка.
След гишето: изгубен поглед, липсващ формуляр, записан час за след 3 месеца."
Пиши на БЪЛГАРСКИ. Кратко и визуално.""",
        "hashtags": "#ПредиСлед #Гише #Бюрокрация",
    },
    {
        "type": "share_if",
        "name": "Сподели ако",
        "prompt": """Напиши КРАТЪК Facebook пост (1-2 изречения) завършващ с "Сподели, ако и на теб ти се е случвало!"
Ситуацията трябва да е универсална бюрократична болка, която всеки е преживял.
Примери:
- "Отиваш на гишето с ВСИЧКИ документи. Оказва се, че ти трябва ОЩЕ ЕДИН, за който никой не ти е казал. Сподели, ако и на теб ти се е случвало!"
- "Звъниш на телефона за информация. Обаждат ти се обратно... след 3 седмици. Сподели, ако и на теб ти се е случвало!"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Сподели #ИНаМен #Бюрокрация",
    },
    {
        "type": "caption_this",
        "name": "Опиши тази ситуация",
        "prompt": """Напиши Facebook пост описващ абсурдна бюрократична ситуация, завършващ с "Как бихте описали тази ситуация с 3 думи? 👇"
Ситуацията трябва да е визуална и комична.
Пример: "Представете си: стоите на опашка 2 часа. Стигате до гишето. Служителката ви казва 'Обедна почивка' и затваря прозорчето пред носа ви. Как бихте описали тази ситуация с 3 думи? 👇"
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#ОпишиС3Думи #Бюрокрация #Хумор",
    },
    {
        "type": "survival_guide",
        "name": "Наръчник за оцеляване",
        "prompt": """Напиши кратък саркастичен "наръчник за оцеляване" пост с 3-5 кратки точки за конкретна бюрократична ситуация.
Формат: "📋 Наръчник за оцеляване: [ситуация]" + точки
Пример:
"📋 Наръчник за оцеляване: Посещение в НАП
1. Вземи си книга. Или две.
2. Зареди телефона до 100%.
3. Не забравяй да ядеш преди — вътре няма кафене.
4. Подготви се морално за изречението 'Системата не работи'.
5. Помни: ти си по-силен от бюрокрацията. Вероятно."
Пиши на БЪЛГАРСКИ.""",
        "hashtags": "#Наръчник #Оцеляване #Бюрокрация",
    },
]


def load_history():
    if SOCIAL_HISTORY_FILE.exists():
        return json.loads(SOCIAL_HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def save_history(history):
    SOCIAL_HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def gemini_call(client, prompt):
    """Single Gemini call with retry + model fallback."""
    for model in MODELS:
        for attempt in range(MAX_API_RETRIES):
            try:
                resp = client.models.generate_content(model=model, contents=prompt)
                return resp.text.strip()
            except Exception as e:
                err = str(e)
                overloaded = any(
                    k in err for k in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]
                )
                if overloaded and attempt < MAX_API_RETRIES - 1:
                    print(f"  {model} attempt {attempt + 1} overloaded, retry in {API_RETRY_DELAY}s")
                    time.sleep(API_RETRY_DELAY)
                elif overloaded:
                    print(f"  {model} exhausted, trying fallback")
                    break
                else:
                    raise
    raise RuntimeError("All models exhausted")


def find_template(template_type):
    for t in POST_TEMPLATES:
        if t["type"] == template_type:
            return t
    raise KeyError(template_type)


def generate_variants(client, template, regen=False):
    task = template["prompt"]
    full = GENERATION_PREAMBLE.format(task=task) + (REGEN_NOTE if regen else "")
    raw = gemini_call(client, full)
    return parse_variants(raw)


def score_variants(client, variants):
    prompt = JUDGE_PROMPT.format(v1=variants[0], v2=variants[1], v3=variants[2])
    raw = gemini_call(client, prompt)
    return parse_scores(raw)


def build_scene_prompt(client, post_text):
    """1-sentence English visual description used as Pollinations/Tenor input."""
    prompt = f"""You will be given a Bulgarian satirical Facebook post about bureaucracy.
Return ONE short English sentence (max 15 words) describing a visual scene for it.
No commentary. No labels. Just the sentence.

Post:
{post_text}"""
    return gemini_call(client, prompt).strip().strip('".')


def slugify_for_file(template_type):
    today = date.today().isoformat()
    return f"{today}-{template_type}"


def make_visual(category_key, template_type, chosen_text, scene_prompt):
    """Dispatch by category visual_type. Returns (image_url, local_path_or_none)."""
    visual_type = CATEGORIES[category_key]["visual_type"]
    slug = slugify_for_file(template_type)

    if visual_type == "gif":
        try:
            url = visuals.fetch_gif(scene_prompt)
            return url, None
        except RuntimeError as e:
            print(f"  GIF fetch failed ({e}); falling back to illustration")
            path = visuals.make_illustration(scene_prompt, slug=slug)
            return f"{SITE_BASE_URL}/images/social/{path.name}", path

    if visual_type == "meme":
        top, bottom = split_meme_text(chosen_text)
        path = visuals.make_meme(top, bottom, scene_prompt, slug=slug)
    elif visual_type == "infographic":
        headline, body = split_infographic_text(chosen_text)
        path = visuals.make_infographic(headline, body, scene_prompt, slug=slug)
    else:
        path = visuals.make_illustration(scene_prompt, slug=slug)

    return f"{SITE_BASE_URL}/images/social/{path.name}", path


def split_meme_text(text):
    """Crude split: first line up, rest down. If single line, put it all bottom."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    lines = [l for l in lines if not l.startswith("#")]
    if not lines:
        return "", text
    if len(lines) == 1:
        return "", lines[0]
    return lines[0], " ".join(lines[1:])


def split_infographic_text(text):
    """First line headline, rest body."""
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    if not lines:
        return "ЗНАЕТЕ ЛИ", text
    return lines[0], " ".join(lines[1:]) if len(lines) > 1 else lines[0]


def run(dry_run=False):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        sys.exit(1)
    client = genai.Client(api_key=api_key)

    history = load_history()
    category_key = pick_category(history)
    template_type = pick_template(category_key, history)
    template = find_template(template_type)

    print(f"Category: {category_key}  Template: {template_type}")

    variants = generate_variants(client, template)
    scores = score_variants(client, variants)
    best_text, total = pick_best(variants, scores)
    print(f"  best score: {total}")

    if total < THRESHOLD:
        print("  below threshold, regenerating once")
        variants = generate_variants(client, template, regen=True)
        scores = score_variants(client, variants)
        best_text, total = pick_best(variants, scores)
        print(f"  regen score: {total}")

    hashtags = template.get("hashtags", "#гише #бюрокрация")
    if "#" not in best_text:
        best_text = f"{best_text}\n\n{hashtags}"

    scene_prompt = build_scene_prompt(client, best_text)
    print(f"  scene: {scene_prompt}")

    image_url, local_path = make_visual(category_key, template_type, best_text, scene_prompt)
    print(f"  visual: {image_url}")

    output = {
        "type": template_type,
        "category": category_key,
        "text": best_text,
        "image_url": image_url,
    }
    out_file = REPO_ROOT / "scripts" / "social-output.json"
    out_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    history.append({
        "type": template_type,
        "category": category_key,
        "date": date.today().isoformat(),
        "score": total,
        "preview": best_text[:100],
    })
    history = history[-50:]
    save_history(history)
    print(f"output: {out_file}")
    if dry_run:
        print("DRY RUN: skipping Buffer step (post_to_buffer.py not invoked here anyway)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
