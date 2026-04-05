from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

import requests
from flask import render_template

from config import Config

DayKey = Literal["yesterday", "today", "tomorrow"]

PAGE_CONFIG = {
    "yesterday": {
        "title": "Матчи за вчера",
        "slug": "yesterday",
        "offset": -1,
        "description": "Результаты и расписание киберспортивных матчей за вчерашний день.",
    },
    "today": {
        "title": "Матчи на сегодня",
        "slug": "today",
        "offset": 0,
        "description": "Киберспортивные матчи на сегодняшний день.",
    },
    "tomorrow": {
        "title": "Матчи на завтра",
        "slug": "tomorrow",
        "offset": 1,
        "description": "Киберспортивные матчи на завтрашний день.",
    },
}

GENERATED_DIR = Path("generated")
GENERATED_DIR.mkdir(exist_ok=True)


def get_target_day_bounds(offset_days: int) -> tuple[str, str, datetime]:
    now_utc = datetime.now(timezone.utc)
    target_date = (now_utc + timedelta(days=offset_days)).date()

    start_dt = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=1)

    start_iso = start_dt.isoformat().replace("+00:00", "Z")
    end_iso = end_dt.isoformat().replace("+00:00", "Z")

    return start_iso, end_iso, start_dt


def build_schema_org(page_title: str, page_description: str, page_url: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": Config.ORG_NAME,
        "url": Config.SITE_URL,
        "logo": Config.ORG_LOGO,
        "sameAs": [],
        "mainEntityOfPage": {
            "@type": "WebPage",
            "name": page_title,
            "description": page_description,
            "url": page_url,
        },
    }


def format_match_time(iso_dt: str | None) -> str:
    if not iso_dt:
        return "Время не указано"

    try:
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
        return dt.strftime("%H:%M UTC")
    except ValueError:
        return iso_dt


def format_match_status(status: str | None) -> str:
    status_map = {
        "finished": "Завершён",
        "running": "В прямом эфире",
        "not_started": "Ожидается",
    }
    return status_map.get(status, status or "Неизвестно")


def fetch_matches_for_day(day_key: DayKey) -> dict:
    if day_key not in PAGE_CONFIG:
        raise ValueError(f"Неизвестный day_key: {day_key}")

    page_data = PAGE_CONFIG[day_key]
    start_iso, end_iso, target_date = get_target_day_bounds(page_data["offset"])

    headers = {
        "Authorization": f"Bearer {Config.PANDASCORE_TOKEN}",
        "Accept": "application/json",
    }

    params = {
        "range[begin_at]": f"{start_iso},{end_iso}",
        "sort": "begin_at",
        "page[size]": 50,
    }

    url = f"{Config.BASE_URL}/matches"

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        raw_matches = response.json()
        api_error = None
    except requests.RequestException as exc:
        raw_matches = []
        api_error = f"Ошибка при обращении к PandaScore API: {exc}"

    matches = []
    for item in raw_matches:
        opponents = item.get("opponents") or []

        team1 = "TBD"
        team2 = "TBD"

        if len(opponents) > 0:
            team1 = opponents[0].get("opponent", {}).get("name") or "TBD"

        if len(opponents) > 1:
            team2 = opponents[1].get("opponent", {}).get("name") or "TBD"

        league = item.get("league") or {}
        serie = item.get("serie") or {}
        tournament = item.get("tournament") or {}
        videogame = item.get("videogame") or {}

        matches.append(
            {
                "id": item.get("id"),
                "name": item.get("name") or f"{team1} vs {team2}",
                "status": format_match_status(item.get("status")),
                "begin_at": format_match_time(item.get("begin_at")),
                "scheduled_at": item.get("scheduled_at"),
                "team1": team1,
                "team2": team2,
                "league_name": league.get("name") or "Unknown League",
                "serie_name": serie.get("full_name") or serie.get("name") or "",
                "tournament_name": tournament.get("name") or "",
                "videogame": videogame.get("name") or "Unknown Game",
                "match_type": item.get("match_type") or "",
                "number_of_games": item.get("number_of_games") or "",
            }
        )

    seo = {
        "title": f"{page_data['title']} | {Config.SITE_NAME}",
        "description": page_data["description"],
        "keywords": f"киберспорт, esports, матчи, {page_data['slug']}, PandaScore",
        "canonical": f"{Config.SITE_URL}/matches/{page_data['slug']}",
        "h1": page_data["title"],
    }

    schema_org = build_schema_org(
        page_title=seo["title"],
        page_description=seo["description"],
        page_url=seo["canonical"],
    )

    return {
        "page_title": page_data["title"],
        "target_date": target_date.strftime("%d.%m.%Y"),
        "matches": matches,
        "slug": page_data["slug"],
        "seo": seo,
        "schema_org": schema_org,
        "api_error": api_error,
    }


def generate_page(day_key: DayKey) -> str:
    data = fetch_matches_for_day(day_key)

    html = render_template(
        "matches_page.html",
        page_title=data["page_title"],
        target_date=data["target_date"],
        matches=data["matches"],
        site_name=Config.SITE_NAME,
        current_slug=data["slug"],
        seo=data["seo"],
        schema_org=data["schema_org"],
    )

    output_path = GENERATED_DIR / f"{data['slug']}.html"
    output_path.write_text(html, encoding="utf-8")

    return str(output_path)


def generate_all_pages() -> list[str]:
    generated_files = []

    for day_key in ["yesterday", "today", "tomorrow"]:
        file_path = generate_page(day_key)
        generated_files.append(file_path)

    return generated_files