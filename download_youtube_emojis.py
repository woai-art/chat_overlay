#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилита для скачивания изображений YouTube-эмоджи и обновления youtube_emojis.json
до локальных путей.

Usage:
    python download_youtube_emojis.py
"""

import json
import os
import re
import sys
import urllib.request
from urllib.error import URLError, HTTPError


EMOJI_JSON_PATH = "youtube_emojis.json"
LOCAL_DIR = "youtube-emojis"
SRC_REGEX = re.compile(r'src="([^"]+)"')


def ensure_directory(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def download_file(url: str, target_path: str) -> None:
    if os.path.exists(target_path):
        return

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
    except HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code} for {url}") from e
    except URLError as e:
        raise RuntimeError(f"Network error for {url}: {e.reason}") from e

    with open(target_path, "wb") as f:
        f.write(data)


def convert_emojis(json_path: str, output_dir: str) -> int:
    with open(json_path, "r", encoding="utf-8") as f:
        emojis = json.load(f)

    ensure_directory(output_dir)
    updated = 0

    for code, html in emojis.items():
        match = SRC_REGEX.search(html)
        if not match:
            continue

        url = match.group(1)
        filename = os.path.basename(url.split("?")[0])
        if not filename:
            filename = f"{code.strip(':').replace('/', '_')}.png"

        local_path = os.path.join(output_dir, filename)
        download_file(url, local_path)

        local_src = f"./{output_dir}/{filename}"
        new_html = html.replace(url, local_src)
        if new_html != html:
            emojis[code] = new_html
            updated += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(emojis, f, ensure_ascii=False, indent=2)

    return updated


def main():
    try:
        updated = convert_emojis(EMOJI_JSON_PATH, LOCAL_DIR)
        print(f"[OK] Обработано эмоджи: {updated}. Файлы сохранены в {LOCAL_DIR}")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

