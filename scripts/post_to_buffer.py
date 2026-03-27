#!/usr/bin/env python3
"""Post the latest article to Facebook via Buffer's GraphQL API."""

import json
import os
import sys
from pathlib import Path
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "scripts" / "output.json"

BUFFER_API = "https://api.buffer.com/rpc"


def get_channel_id(headers):
    """Find the Гише ∞ Facebook channel."""
    # Get org ID
    resp = requests.post(
        BUFFER_API,
        headers=headers,
        json={"query": "{ account { organizations { id name } } }"},
        timeout=15,
    )
    resp.raise_for_status()
    orgs = resp.json()["data"]["account"]["organizations"]
    org_id = orgs[0]["id"]

    # Get channels
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

    # Find Facebook channel
    for ch in channels:
        if ch["service"] == "facebook":
            return ch["id"]

    print("ERROR: No Facebook channel found in Buffer")
    sys.exit(1)


def create_post(headers, channel_id, text, image_url):
    """Create and publish a post via Buffer."""
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
        "variables": {
            "input": {
                "channelId": channel_id,
                "text": text,
                "schedulingType": "automatic",
                "mode": "shareNow",
                "metadata": {"facebook": {"type": "post"}},
                "assets": {"images": [{"url": image_url}]},
                "source": "api",
            }
        },
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


def main():
    buffer_key = os.environ.get("BUFFER_API_KEY")
    if not buffer_key:
        print("ERROR: BUFFER_API_KEY not set")
        sys.exit(1)

    if not OUTPUT_FILE.exists():
        print("ERROR: output.json not found — run generate_poem.py first")
        sys.exit(1)

    output = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    headers = {
        "Authorization": f"Bearer {buffer_key}",
        "Content-Type": "application/json",
    }

    channel_id = get_channel_id(headers)
    print(f"Channel: {channel_id}")

    # Build post text
    teaser = output.get("teaser", "")
    article_url = output["article_url"]

    if teaser and "{link}" in teaser:
        post_text = teaser.replace("{link}", article_url)
    else:
        post_text = f"""{output['title']}

{teaser if teaser else 'Нова статия в Гише ∞!'}

{article_url}

#бюрокрация #сатира #гише #България"""

    image_url = output["image_url"]

    print(f"Posting to Facebook...")
    create_post(headers, channel_id, post_text, image_url)
    print("Done!")


if __name__ == "__main__":
    main()
