#!/usr/bin/env python3
"""Fetch free arXiv full text (HTML preferred, PDF extract fallback). Persist under fulltext/."""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path

UA = "arxiv-census-fulltext/1.0 (Dec1 prove-out; free fulltext; respects rate limits)"
SLEEP_S = 3.5
ROOT = Path(__file__).resolve().parent
# Prefer /tmp for bulky text; record store-relative path when mirrored
TMP_FULLTEXT = Path("/tmp/arxiv-census/fulltext")
STORE_FULLTEXT = ROOT / "fulltext"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "header", "footer"}:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "header", "footer"} and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        t = data.strip()
        if t:
            self.parts.append(t)


def id_to_path_key(arxiv_id: str) -> str:
    # astro-ph/9204001 -> astro-ph_9204001 ; 0905.0001 stays
    return arxiv_id.replace("/", "_")


def _get(url: str, timeout: int = 120) -> tuple[int, bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(), resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b"", ""
    except Exception:
        return 0, b"", ""


def html_to_text(html: bytes) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html.decode("utf-8", errors="replace"))
    except Exception:
        return ""
    return " ".join(parser.parts)


def pdf_to_text(pdf: bytes, max_pages: int = 40) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(BytesIO(pdf))
        parts = []
        for i, page in enumerate(reader.pages):
            if i >= max_pages:
                break
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except Exception:
        return ""


def fetch_fulltext(arxiv_id: str, *, sleep: float = SLEEP_S) -> dict:
    """
    Returns dict with keys: ok, source, text, sha256, path, bytes, error
    Saves extracted text to TMP_FULLTEXT/<key>/text.txt (+ meta.json).
    """
    key = id_to_path_key(arxiv_id)
    out_dir = TMP_FULLTEXT / key
    out_dir.mkdir(parents=True, exist_ok=True)
    text = ""
    source = ""
    err = ""
    raw_bytes = 0

    # Prefer native HTML (arxiv.org/html), then ar5iv, then PDF
    candidates = [
        (f"https://arxiv.org/html/{arxiv_id}", "html"),
        (f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}", "ar5iv"),
        (f"https://arxiv.org/pdf/{arxiv_id}", "pdf"),
    ]
    for url, kind in candidates:
        time.sleep(sleep)
        status, body, ctype = _get(url)
        if status != 200 or not body:
            err = f"{kind}:{status}"
            continue
        raw_bytes = len(body)
        if kind in {"html", "ar5iv"} or "html" in (ctype or ""):
            text = html_to_text(body)
            # Reject tiny/boilerplate-only pages
            if len(text) < 500:
                err = f"{kind}:too_short"
                continue
            source = kind
            break
        if kind == "pdf" or "pdf" in (ctype or ""):
            text = pdf_to_text(body)
            if len(text) < 200:
                err = f"pdf:extract_short"
                continue
            source = "pdf"
            break

    if not text:
        meta = {
            "arxiv_id": arxiv_id,
            "ok": False,
            "error": err or "fetch_failed",
            "source": None,
            "path": None,
            "sha256": None,
            "chars": 0,
        }
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        return meta

    text_path = out_dir / "text.txt"
    text_path.write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    # relative path from ledger root for portability
    rel = f"fulltext/{key}/text.txt"
    # best-effort mirror meta+tiny pointer into store (not full text if huge)
    store_dir = STORE_FULLTEXT / key
    try:
        store_dir.mkdir(parents=True, exist_ok=True)
        # store text if < 2MB else pointer only
        if len(text.encode("utf-8")) < 2_000_000:
            (store_dir / "text.txt").write_text(text, encoding="utf-8")
        else:
            (store_dir / "text.txt.ptr").write_text(
                json.dumps({"tmp": str(text_path), "sha256": sha, "chars": len(text)}) + "\n",
                encoding="utf-8",
            )
    except OSError as e:
        err = f"store_mirror:{e}"

    meta = {
        "arxiv_id": arxiv_id,
        "ok": True,
        "source": source,
        "path": rel,
        "abs_path": str(text_path),
        "sha256": sha,
        "chars": len(text),
        "raw_bytes": raw_bytes,
        "error": err or None,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    try:
        (store_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    except Exception:
        pass
    return meta


if __name__ == "__main__":
    import sys

    aid = sys.argv[1] if len(sys.argv) > 1 else "0905.0001"
    print(json.dumps({k: v for k, v in fetch_fulltext(aid, sleep=1.0).items() if k != "abs_path"}, indent=2))
