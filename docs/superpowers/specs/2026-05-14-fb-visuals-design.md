# Facebook Posts: Visuals + Categories + Humor Quality

**Date:** 2026-05-14
**Status:** Draft, pending review

## Problem

Current `generate_social.py` produces text-only Facebook posts for 26 of 27 templates. Only `old_article_hook` attaches an image (reusing the cover of an old article). Last 10 posts on the page have no visual element. Result: low scroll-stop value, weak shareability, no brand consistency on the timeline.

Goals:
1. Every social post has a visual (image or GIF).
2. Posts grouped into 4 clear categories with distinct visual treatments.
3. Humor quality high enough to make a reader laugh in a quiet office and feel compelled to share.

Non-goals:
- Changing posting frequency or schedule.
- Editing the poem pipeline.
- Multi-platform posting (Instagram, TikTok). Facebook only.

## Categories

Consolidate the 27 templates into 4 categories. Each category fixes a visual treatment.

| Category | Templates (existing) | Visual type | Source |
|---|---|---|---|
| 🧠 МЕМЕТА | `meme_text`, `weekend_meme`, `before_after`, `share_if`, `pro_tip`, `bureaucrat_quote` | Illustration + top/bottom Impact-style Cyrillic overlay | Pollinations + PIL |
| 💡 ЗНАЕТЕ ЛИ ЧЕ | `did_you_know_real`, `satirical_fact`, `historical_bureaucracy`, `bureaucracy_bingo` | Illustration + boxed text block (infographic-style) | Pollinations + PIL |
| 🤪 АБСУРДИ | `current_absurdity`, `comparison`, `personification`, `educational_satire`, `survival_guide`, `caption_this`, `behind_the_scenes`, `old_article_hook` | Clean Доньо Донев b/w + red accent illustration, no text overlay | Pollinations |
| 🎬 РЕАКЦИИ | `interactive_poll`, `engaging_question`, `tag_a_friend`, `this_or_that`, `finish_the_sentence`, `theme_song`, `user_stories`, `weekend_humor`, `monthly_reflection` | GIF | Tenor API |

Picker logic: round-robin across categories (not random) so feed shows variety. Within category, random template from those not used in last 6 posts.

## Architecture

### New files

**`scripts/categories.py`** — single source of truth.
- `CATEGORIES`: dict mapping category key (`memes` | `did_you_know` | `absurdi` | `reactions`) to `{name, emoji, visual_type, templates: [...]}`.
- `pick_category(history)`: round-robin selection based on last 4 posts in history.
- `pick_template(category, history)`: random from templates not in last 6.

**`scripts/visuals.py`** — visual generation.
- `make_meme(top_text, bottom_text, scene_prompt) -> Path`: fetch Pollinations Доньо Донев illustration, overlay top/bottom Cyrillic text with PIL Impact-equivalent font. Save to `static/images/social/<date>-<slug>.jpg`.
- `make_infographic(headline, body, scene_prompt) -> Path`: Pollinations illustration with a white-bordered text block at bottom.
- `make_illustration(scene_prompt) -> Path`: clean Pollinations illustration, no overlay.
- `fetch_gif(keywords) -> str`: Tenor v2 API search, returns direct GIF URL. Bulgarian post text gets translated to English keywords inside Gemini call before search.

Font: bundle a Cyrillic-capable bold sans (e.g., DejaVuSans-Bold or Roboto-Black) in `scripts/fonts/`. Stroke effect via PIL `ImageDraw.text(stroke_width=4, stroke_fill='black', fill='white')`.

### Modified files

**`scripts/generate_social.py`** — rewritten control flow:
1. Load history.
2. `category = pick_category(history)`.
3. `template = pick_template(category, history)`.
4. Generate **3 text variants** in one Gemini call (prompt asks for exactly 3 variants separated by `---`).
5. Score each variant in one Gemini call:
   ```
   Оцени всеки от 3 поста по 2 критерия (1-10):
   - laugh: ще накара ли някой да се изсмее тихо в офис?
   - share: ще го сподели ли с приятел?
   Върни JSON: [{"laugh":N,"share":N}, ...]
   ```
6. Pick variant with highest `laugh + share`.
7. If max sum < 14 → regenerate text once (single retry).
8. Build a `scene_prompt` for the visual: a separate small Gemini call that translates the chosen post into a 1-sentence visual description in English.
9. Dispatch to visual generator by category visual_type.
10. Write `scripts/social-output.json` with `text` and `image_url` (local file path served by GitHub Pages, or Tenor URL).

**`scripts/post_to_buffer.py`** — unchanged. Already handles `image_url` for any post.

**`scripts/requirements.txt`** — add `Pillow`.

**`.github/workflows/social-post.yml`**:
- Add `static/images/social/` to `git add`.
- Add `TENOR_API_KEY` env to "Post to Buffer" or generate step:
  ```yaml
  env:
    TENOR_API_KEY: ${{ secrets.TENOR_API_KEY }}
  ```

### New repo secrets

- `TENOR_API_KEY` — free key from Google Cloud Console (Tenor API enabled). User adds via GitHub repo settings before first run.

### Asset hosting

- Memes / infographics / illustrations: PIL-composed JPG saved to `static/images/social/<YYYY-MM-DD>-<category>-<slug>.jpg`, committed by the workflow, served at `https://gisheto.com/images/social/<filename>.jpg`. Surfaces in Hugo output via the `static/` convention.
- Tenor GIFs: direct CDN URL, not committed. Tenor URLs are stable.

## Humor Quality Mechanism

Best-of-3 with judge model.

**Generation prompt (per template) gains a fixed preamble:**

```
Ти си български сатирик. Целта ти: пост който кара читателя ДА СЕ ИЗСМЕЕ ТИХО НА ТЕЛЕФОНА В ОФИСА.
Не общи фрази, а специфични. Ползвай:
- Конкретни институции: НАП, КАТ, БДЖ, ЕОН/ЧЕЗ, общината, "областна"
- Конкретни моменти: "елате утре", "системата не работи", "не съм оторизирана", "този прозорец не работи", "обедна почивка от 10:05 до 17:00"
- Конкретни абсурди: печат върху печат, формуляр в 3 копия, час за след 3 месеца, гише 7
- Конкретни хора: "леля на гише 3", "охранителят който не знае нищо"

Избягвай: "Опа, бюрокрация!", "Браво на администрацията!", общи философски заключения.
Бъди КОНКРЕТЕН. Образът да е виден. Шегата да е остра.

Сега, ето задачата:
[template prompt]

ВЪРНИ 3 ВАРИАНТА разделени с ред "---". Без номерация. Без обяснения. Само трите поста.
```

**Judge prompt:**

```
Ти си строг редактор на сатиричен портал. Имаш 3 варианта на Facebook пост.
Оцени всеки 1-10 по два критерия:
- laugh: реално ли е смешно (1=не, 10=ще се смея на глас)
- share: бих ли го споделил с приятел (1=не, 10=веднага)

Бъди строг. Средното не е 7 — средното е 4.

Варианти:
1. [text 1]
2. [text 2]
3. [text 3]

Върни САМО JSON масив: [{"laugh":N,"share":N},{"laugh":N,"share":N},{"laugh":N,"share":N}]
```

Threshold: 14/20. If max combined < 14 → one regeneration attempt with the prompt note "Предишните бяха слаби. Бъди по-конкретен и по-остър."

## Data Flow

```
social-post.yml schedule trigger
  → generate_social.py
      → pick_category(history)
      → pick_template(category, history)
      → Gemini: 3 text variants
      → Gemini: score variants → pick best (regen if max<14)
      → Gemini: scene_prompt for visual (1 sentence English)
      → visuals.py: dispatch by category.visual_type
          memes        → make_meme()        → static/images/social/...jpg
          did_you_know → make_infographic() → static/images/social/...jpg
          absurdi      → make_illustration()→ static/images/social/...jpg
          reactions    → fetch_gif()        → tenor_cdn_url
      → write social-output.json {text, image_url}
  → post_to_buffer.py social
      → Buffer GraphQL createPost with assets.images[0].url
  → workflow commits static/images/social/ + social-history.json
```

## Error Handling

- Pollinations 5xx / timeout: retry 3x with 10s backoff. On final failure, fall back to category=absurdi with stock illustration URL from the most recent successful post.
- Tenor empty result: re-search with simpler English keyword (e.g., "frustrated"). If still empty, fall back to make_illustration().
- Gemini judge returns malformed JSON: fall back to picking variant 1 (no scoring).
- PIL font missing: fail workflow with clear error (font is bundled, missing = bug).
- Post-already-published / duplicate Buffer error: log and exit 0 (do not retry; next cron handles it).

## Testing

- Local dry-run mode (`--dry-run` flag on `generate_social.py`): runs full pipeline, saves output to disk, **does not** call Buffer. Manual visual inspection of `social-output.json` and the generated image.
- Manual workflow_dispatch trigger on `social-post.yml` after merge.
- Verify in Buffer's posted feed that image attaches before crediting fix as done.

## Rollout

Single PR. Merge, manually trigger `social-post.yml`, inspect resulting post on the Facebook page, confirm image renders.

If issues, rollback: revert PR. No data migration required (history file format unchanged).

## Open Questions / Future

- Engagement layer (poll widgets, native FB poll API) — out of scope, deferred.
- A/B testing variants directly on Facebook — needs platform reach data we don't have yet.
- Translating Tenor results back to Cyrillic captions on the GIF — possible later via PIL overlay on first frame, skipped for now.
