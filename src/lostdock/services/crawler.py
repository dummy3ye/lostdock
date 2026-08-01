"""URL re-crawler: fetch stored results and check live status."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional

import requests

log = logging.getLogger(__name__)


@dataclass
class CrawlReport:
    url: str
    status_code: Optional[int]
    http_title: str
    content_type: str
    size: int
    ok: bool
    error: str = ""
    original_url: str = ""


def crawl_url(
    url: str,
    session: Optional[requests.Session] = None,
    timeout: float = 15.0,
    user_agent: str = "Mozilla/5.0 (lostdock-research)",
) -> CrawlReport:
    """Fetch a URL and extract status/title/size. Never raises."""
    session = session or requests.Session()
    try:
        resp = session.get(url, timeout=timeout, headers={"User-Agent": user_agent}, allow_redirects=True)
        title = ""
        if "text/html" in resp.headers.get("content-type", ""):
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(resp.text[:200_000], "html.parser")
            t = soup.find("title")
            if t:
                title = t.get_text(" ", strip=True)[:200]
        content_type = resp.headers.get("content-type", "").split(";")[0]
        return CrawlReport(
            url=resp.url or url,
            status_code=resp.status_code,
            http_title=title,
            content_type=content_type,
            size=len(resp.content),
            ok=200 <= resp.status_code < 400,
            original_url=url,
        )
    except requests.RequestException as exc:
        log.debug("crawl failed %s: %s", url, exc)
        return CrawlReport(url=url, status_code=None, http_title="", content_type="", size=0, ok=False, error=str(exc), original_url=url)


def crawl_many(
    urls: Iterable[str],
    delay: float = 0.4,
    jitter: float = 0.3,
    on_report: Optional[Callable[[CrawlReport], None]] = None,
    limit: Optional[int] = None,
) -> List[CrawlReport]:
    """Crawl many URLs with politeness delay. Callback receives each report."""
    reports: List[CrawlReport] = []
    session = requests.Session()
    for url in urls:
        if limit is not None and len(reports) >= limit:
            break
        report = crawl_url(url, session=session)
        reports.append(report)
        if on_report:
            on_report(report)
        if delay > 0:
            import time

            time.sleep(delay + random.uniform(0, jitter))
    return reports
