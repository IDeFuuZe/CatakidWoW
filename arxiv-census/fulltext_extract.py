#!/usr/bin/env python3
"""
Download arXiv PDF (HTML fallback) and extract ALL text characters.
Primary: pdftotext; secondary: pdfminer; QA compares lengths.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

UA = "arxiv-census-fulltext/2.0 (full-PDF extract; Dec1; rate-limited)"
SLEEP = 3.5
ROOT = Path(__file__).resolve().parent
TMP_FT = Path("/tmp/arxiv-census/fulltext")
STORE_FT = ROOT / "fulltext"
TMP_FT.mkdir(parents=True, exist_ok=True)
STORE_FT.mkdir(parents=True, exist_ok=True)


def id_key(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def _http_get(url: str, timeout: int = 180) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b""
    except Exception:
        return 0, b""


def pdftotext_extract(pdf_path: Path) -> str:
    """Extract all text via poppler pdftotext — no page limit."""
    out = pdf_path.with_suffix(".pdftotext.txt")
    # -raw preserves reading order content; also try -layout and keep longer
    texts = []
    for args in (
        ["pdftotext", "-raw", "-enc", "UTF-8", str(pdf_path), str(out)],
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), str(out.with_suffix(".layout.txt"))],
    ):
        try:
            subprocess.run(args, check=True, capture_output=True, timeout=300)
            p = Path(args[-1])
            if p.exists():
                texts.append(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
    if not texts:
        return ""
    return max(texts, key=len)


def pdfminer_extract(pdf_path: Path, *, timeout_s: float = 90.0) -> str:
    """pdfminer can hang on pathological PDFs — hard-timeout via subprocess."""
    import multiprocessing as mp

    def _worker(path: str, q: mp.Queue) -> None:
        try:
            from pdfminer.high_level import extract_text

            q.put(extract_text(path) or "")
        except Exception:
            q.put("")

    try:
        q: mp.Queue = mp.Queue()
        proc = mp.Process(target=_worker, args=(str(pdf_path), q))
        proc.start()
        proc.join(timeout_s)
        if proc.is_alive():
            proc.terminate()
            proc.join(5)
            if proc.is_alive():
                proc.kill()
            return ""
        if not q.empty():
            return q.get() or ""
        return ""
    except Exception:
        return ""


def html_extract(html: bytes) -> str:
    # Strip tags naively but keep all text nodes (zero intentional truncation)
    from html.parser import HTMLParser

    class P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts: list[str] = []
            self.skip = 0

        def handle_starttag(self, tag, attrs):
            if tag in {"script", "style"}:
                self.skip += 1

        def handle_endtag(self, tag):
            if tag in {"script", "style"} and self.skip:
                self.skip -= 1

        def handle_data(self, data):
            if not self.skip:
                self.parts.append(data)

    p = P()
    try:
        p.feed(html.decode("utf-8", errors="replace"))
    except Exception:
        return html.decode("utf-8", errors="replace")
    return "".join(p.parts)


def qa_flags(text: str, pdf_bytes: int) -> list[str]:
    flags = []
    if not text or not text.strip():
        flags.append("EXTRACT_EMPTY")
    elif len(text.strip()) < 200:
        flags.append("EXTRACT_TOO_SHORT")
    # Garbled heuristic: very high non-printable / replacement ratio
    if text:
        bad = sum(1 for ch in text if ch == "\ufffd" or (ord(ch) < 9))
        if bad / max(len(text), 1) > 0.02:
            flags.append("EXTRACT_GARBLED")
    if pdf_bytes > 50_000 and len(text.strip()) < 500:
        flags.append("OCR_NEEDED")
    if not flags:
        flags.append("EXTRACT_OK")
    return flags


def extract_arxiv(arxiv_id: str, *, sleep: float = SLEEP) -> dict:
    """
    Download PDF, extract ALL text, save fulltext/<key>.txt (+ .pdf).
    Returns metadata dict (ok, path, sha256, chars, extractor, flags, ...).
    """
    key = id_key(arxiv_id)
    work = TMP_FT / key
    work.mkdir(parents=True, exist_ok=True)
    pdf_path = work / f"{key}.pdf"
    txt_path = work / f"{key}.txt"
    # Also canonical store names: fulltext/<key>.txt
    store_txt = STORE_FT / f"{key}.txt"
    store_pdf = STORE_FT / f"{key}.pdf"

    time.sleep(sleep)
    status, pdf = _http_get(f"https://arxiv.org/pdf/{arxiv_id}")
    source = "pdf"
    text = ""
    extractor = None
    flags: list[str] = []

    if status == 200 and pdf.startswith(b"%PDF"):
        pdf_path.write_bytes(pdf)
        t1 = pdftotext_extract(pdf_path)
        # Skip pdfminer when pdftotext already yielded a long extract (avoids multi-hour hangs)
        if len(t1.strip()) >= 5000:
            t2 = ""
        else:
            t2 = pdfminer_extract(pdf_path, timeout_s=90.0)
            if not t2 and len(t1.strip()) < 500:
                flags.append("PDFMINER_TIMEOUT_OR_EMPTY")
        # Keep the longer extract — never truncate
        if len(t1) >= len(t2):
            text, extractor = t1, "pdftotext"
        else:
            text, extractor = t2, "pdfminer"
        if t1 and t2 and abs(len(t1) - len(t2)) / max(len(t1), len(t2), 1) > 0.25:
            flags.append("EXTRACTOR_LEN_MISMATCH")
        flags.extend(qa_flags(text, len(pdf)))
    else:
        # HTML / abs-page fallback when PDF missing (legacy ids sometimes 404 PDF)
        html_ok = False
        for kind, url in (
            ("html", f"https://arxiv.org/html/{arxiv_id}"),
            ("ar5iv", f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"),
            ("abs", f"https://arxiv.org/abs/{arxiv_id}"),
        ):
            time.sleep(sleep)
            st, html = _http_get(url)
            if st != 200 or not html:
                continue
            text = html_extract(html)
            if len(text.strip()) < 200:
                continue
            extractor = kind
            source = kind
            flags.extend(qa_flags(text, len(html)))
            flags.append(f"pdf_http_{status}_fell_back_{kind}")
            html_ok = True
            break
        if not html_ok:
            flags = ["EXTRACT_FAIL", f"pdf_http_{status}", "html_fallback_failed"]

    ok = bool(text.strip()) and "EXTRACT_FAIL" not in flags and "EXTRACT_EMPTY" not in flags
    if "OCR_NEEDED" in flags and len(text.strip()) < 200:
        ok = False

    sha = hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None
    if text:
        txt_path.write_text(text, encoding="utf-8")  # full text, zero truncation
        try:
            store_txt.write_text(text, encoding="utf-8")
        except OSError:
            # store may reject large files — keep tmp + pointer
            try:
                store_txt.write_text(
                    json.dumps({"tmp": str(txt_path), "sha256": sha, "chars": len(text)}) + "\n",
                    encoding="utf-8",
                )
            except OSError:
                pass
    if pdf_path.exists():
        try:
            if pdf_path.stat().st_size < 5_000_000:
                store_pdf.write_bytes(pdf_path.read_bytes())
        except OSError:
            pass

    meta = {
        "arxiv_id": arxiv_id,
        "ok": ok,
        "source": source,
        "extractor": extractor,
        "path": f"fulltext/{key}.txt",
        "abs_path": str(txt_path if text else ""),
        "pdf_path": str(pdf_path) if pdf_path.exists() else None,
        "sha256": sha,
        "chars": len(text),
        "pdf_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0,
        "flags": flags,
        "scored_from": "fulltext" if ok else "none",
    }
    (work / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    try:
        (STORE_FT / f"{key}.meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    return meta


if __name__ == "__main__":
    import sys

    aid = sys.argv[1] if len(sys.argv) > 1 else "hep-th/9901001"
    m = extract_arxiv(aid, sleep=1.0)
    print(json.dumps({k: v for k, v in m.items() if k != "abs_path"}, indent=2))
