from flask import Flask, abort, render_template

from config import Config
from generator import fetch_matches_for_day, generate_all_pages

app = Flask(__name__)

VALID_SLUGS = {"yesterday", "today", "tomorrow"}


@app.route("/")
def home():
    return render_template("admin.html")


@app.route("/generate")
def generate():
    generated_files = generate_all_pages()

    return render_template(
        "generate_result.html",
        generated_files=generated_files,
    )


@app.route("/matches/<slug>")
def matches_page(slug: str):
    if slug not in VALID_SLUGS:
        abort(404)

    data = fetch_matches_for_day(slug)

    return render_template(
        "matches_page.html",
        page_title=data["page_title"],
        target_date=data["target_date"],
        matches=data["matches"],
        site_name=Config.SITE_NAME,
        current_slug=slug,
        seo=data["seo"],
        schema_org=data["schema_org"],
        api_error=data["api_error"],
    )


if __name__ == "__main__":
    app.run(debug=True)