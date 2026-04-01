# Claude API Migration + Quality Review Step

**Date:** 2026-04-01
**Scope:** `generate_poem.py`, `requirements.txt`, workflow files
**Status:** Approved

## Summary

Replace Google Gemini with Claude API (Anthropic SDK) in the poem generation pipeline and add a score-and-rewrite quality review step before publishing. Keep the same output format and file structure.

## Architecture

```
pick_topic (Sonnet) → generate_poem (Opus) → review_and_score (Opus) → generate_metadata (Sonnet) → create_article → placeholder_image → update_history
```

The new `review_and_score` step sits between generation and metadata. If the draft scores below 7/10, Opus rewrites it incorporating its own feedback. Max 2 retries. After retries exhausted, the highest-scoring version is used.

## Model Assignment

| Step              | Model                | Reason                         |
|-------------------|----------------------|--------------------------------|
| `pick_topic`      | claude-sonnet-4-6 | Simple selection task          |
| `generate_poem`   | claude-opus-4-6   | Creative writing quality       |
| `review_and_score` | claude-opus-4-6  | Needs literary judgment        |
| `generate_metadata`| claude-sonnet-4-6 | Structured data extraction     |

## Review Step

The reviewer receives the draft + original style prompt and returns JSON:

```json
{
  "score": 8,
  "satire": "strong escalating absurdity",
  "language": "natural Bulgarian, good use of particles",
  "originality": "fresh angle on topic",
  "verdict": "publish",
  "feedback": null
}
```

- `score`: 1-10 overall quality
- `verdict`: `"publish"` or `"rewrite"`
- `feedback`: null if publishing, specific rewrite instructions if rewriting
- If `verdict` is `"rewrite"`, the feedback is passed back to `generate_poem` as additional instructions along with the original prompt
- The rewrite loop runs max 2 times; after that, the highest-scoring version is published

## Style Prompt

Unchanged from current `STYLE_PROMPT` — Bulgarian satirical feuilleton in the tradition of Ivo Siromahov, Elenko Elenkov, "Evala be, mitnitsa" style. 300-600 words.

## Image Prompt Updates

The `image_prompt` field in metadata generation uses this template:

> "Detailed English prompt for black-and-white ink cartoon illustration in minimalist satirical style with bold lines and exaggerated figures, illustrating this specific story. No signatures or artist names anywhere on the image. Any text in the image must be in Bulgarian."

Changes from current:
- Removed "Donio Donev style" name reference (keep the aesthetic, not the attribution)
- Added explicit "No signatures or artist names anywhere on the image"
- Kept "Any text in the image must be in Bulgarian"

## Error Handling

- API call failures: retry once with 5s delay, then fail the workflow
- JSON parse failures on metadata/review: retry once with stricter prompt
- All retries logged to stdout for GitHub Actions visibility

## File Changes

### `requirements.txt`
- Remove: `google-genai>=1.0.0`
- Add: `anthropic>=0.40.0`
- Keep: `requests>=2.31.0`, `Pillow>=10.0.0`

### `generate_poem.py`
Full rewrite. Same external interface:
- Reads `ANTHROPIC_API_KEY` env var (was `GEMINI_API_KEY`)
- Writes same output files: `content/article/{slug}.md`, `static/images/{slug}.jpeg`, `scripts/output.json`, `content/topics-history.json`
- Same functions: `pick_topic`, `generate_poem`, `generate_metadata`, `create_article`, `create_placeholder_image`, `main`
- New function: `review_and_score`
- Helper: `call_claude(model, system, prompt)` wrapping API calls with retry

### `.github/workflows/generate-poem.yml`
- Replace `GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}` with `ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}`

### `.github/workflows/social-post.yml`
- No changes in this step (social script migration is a separate task)

### `post_to_buffer.py`
- No changes

## Out of Scope

- `generate_social.py` migration (next task)
- Image generation with AI (stays as placeholder)
- Any Hugo theme or config changes
