#!/usr/bin/env python3
"""Post to Facebook via Buffer's GraphQL API.

Supports two modes:
  - Article post: image + teaser + link (from output.json)
  - Social post: text-only or text + old article image (from social-output.json)
"""

import json
import os
import sys
from pathlib import Path
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
BUFFER_API = "https://api.buffer.com/rpc"


def get_channel_id(headers):
    """Find the Гише ∞ Facebook channel."""
    resp = requests.post(
        BUFFER_API,
        headers=headers,
        json={"query": "{ account { organizations { id name } } }"},
        timeout=15,
    )
    resp.raise_for_status()
    orgs = resp.json()["data"]["account"]["organizations"]
    org_id = orgs[0]["id"]

    resp = requests.post(
        BUFFER_API,
        headers=headers,
        json={
            "query": """
                query($input: ChannelsInput!) {
                    channels(input: $input) { id name service }
                }
            """,
            "variables": {"input": {"organizationId": org_id}},
        },
        timeout=15,
    )
    resp.raise_for_status()
    channels = resp.json()["data"]["channels"]

    for ch in channels:
        if ch["service"] == "facebook":
            return ch["id"]

    print("ERROR: No Facebook channel found in Buffer")
    sys.exit(1)


def create_post(headers, channel_id, text, image_url=None):
    """Create and publish a post via Buffer."""
    post_input = {
        "channelId": channel_id,
        "text": text,
        "schedulingType": "automatic",
        "mode": "shareNow",
        "metadata": {"facebook": {"type": "post"}},
        "source": "api",
    }

    if image_url:
        post_input["assets"] = {"images": [{"url": image_url}]}

    mutation = {
        "query": """
            mutation CreatePost($input: CreatePostInput!) {
                createPost(input: $input) {
                    ... on PostActionSuccess {
                        post { id status }
                    }
                    ... on NotFoundError { message }
                    ... on UnauthorizedError { message }
                    ... on UnexpectedError { message }
                    ... on RestProxyError { message }
                    ... on LimitReachedError { message }
                    ... on InvalidInputError { message }
                }
            }
        """,
        "variables": {"input": post_input},
    }

    resp = requests.post(BUFFER_API, headers=headers, json=mutation, timeout=30)
    resp.raise_for_status()
    result = resp.json()

    create_data = result.get("data", {}).get("createPost", {})
    if "post" in create_data:
        post = create_data["post"]
        print(f"Post created: id={post['id']}, status={post['status']}")
        return post
    else:
        error_msg = create_data.get("message", json.dumps(result))
        print(f"ERROR: {error_msg}")
        sys.exit(1)


def post_article(headers, channel_id):
    """Post a new article with image + teaser."""
    output_file = REPO_ROOT / "scripts" / "output.json"
    if not output_file.exists():
        print("ERROR: output.json not found")
        sys.exit(1)

    output = json.loads(output_file.read_text(encoding="utf-8"))

    teaser = output.get("teaser", "")
    article_url = output["article_url"]

    if teaser and "{link}" in teaser:
        post_text = teaser.replace("{link}", article_url)
    else:
        post_text = f"""{output['title']}

{teaser if teaser else 'Нова статия в Гише ∞!'}

{article_url}

#бюрокрация #сатира #гише #България"""

    create_post(headers, channel_id, post_text, output.get("image_url"))


def post_social(headers, channel_id):
    """Post a social-only post (meme, hook, quote, etc.)."""
    output_file = REPO_ROOT / "scripts" / "social-output.json"
    if not output_file.exists():
        print("ERROR: social-output.json not found")
        sys.exit(1)

    output = json.loads(output_file.read_text(encoding="utf-8"))

    text = output["text"]
    image_url = output.get("image_url")

    create_post(headers, channel_id, text, image_url)


def main():
    buffer_key = os.environ.get("BUFFER_API_KEY")
    if not buffer_key:
        print("ERROR: BUFFER_API_KEY not set")
        sys.exit(1)

    mode = sys.argv[1] if len(sys.argv) > 1 else "article"

    headers = {
        "Authorization": f"Bearer {buffer_key}",
        "Content-Type": "application/json",
    }

    channel_id = get_channel_id(headers)
    print(f"Channel: {channel_id}")
    print(f"Mode: {mode}")

    if mode == "social":
        post_social(headers, channel_id)
    else:
        post_article(headers, channel_id)

    print("Done!")


if __name__ == "__main__":
    main()
