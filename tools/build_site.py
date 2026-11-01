#!/usr/bin/env python3
"""Builds the Steelhold site pages from tools/locales/<code>.py.

    python3 -I tools/build_site.py          # from the repo root

English pages go to the repo root; each other locale to its own folder (de/, fr/, ...).
A locale listed in PUBLISHED appears in the language links and hreflang tags;
every other locale is built as a draft: noindex, and not linked from anywhere.
Edit the copy in tools/locales/*.py, never in the generated .html files.
"""
import html
import importlib.util
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://frolma.github.io/steelhold-desc-and-privacy/"
STORE = "https://apps.apple.com/app/id6780880608"
MAIL = "val.mail.dev@gmail.com"

# code: (folder, html lang, og locale, name in its own language)
LOCALES = {
    "en": ("", "en", "en_US", "English"),
    "de": ("de/", "de", "de_DE", "Deutsch"),
    "fr": ("fr/", "fr", "fr_FR", "Français"),
    "es-mx": ("es-mx/", "es-MX", "es_MX", "Español (México)"),
    "ja": ("ja/", "ja", "ja_JP", "日本語"),
    "ko": ("ko/", "ko", "ko_KR", "한국어"),
}
# Only the owner adds a locale here, after approving its copy.
PUBLISHED = ["en"]

# name: (folder-relative stem, widths, intrinsic w, h, fallback width)
SHOTS = {
    "iphone": ([480, 800], 1320, 2868, 480),
    "ipad": ([600], 2064, 2752, 600),
    "duo": ([640, 1100], 2853, 2007, 640),
}


def load(code):
    path = ROOT / "tools" / "locales" / f"{code.replace('-', '_')}.py"
    spec = importlib.util.spec_from_file_location(code, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.T


def ui(s):
    """[[MENU]] -> <span class="ui">MENU</span>; › -> styled separator."""
    s = re.sub(r"\[\[(.+?)\]\]", lambda m: f'<span class="ui">{m.group(1)}</span>', s)
    return s.replace(" › ", ' <span class="sep">›</span> ')


def esc(s):
    return html.escape(s, quote=True)


def pic(r, kind, name, alt, sizes, eager=False):
    widths, w, h, fb = SHOTS[kind]
    stem = f"{r}assets/img/{kind}-{name}"
    def srcset(ext):
        return ", ".join(f"{stem}-{x}.{ext} {x}w" for x in widths)
    load_attr = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img src="{stem}-{fb}.jpg" width="{w}" height="{h}" alt="{esc(alt)}" {load_attr} decoding="async"></picture>')


def phone(r, name, alt, sizes, cls="", eager=False):
    return f'<div class="phone {cls}">{pic(r, "iphone", name, alt, sizes, eager)}</div>'


ICON_OPEN = '<svg class="icon-open" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
ICON_CLOSE = '<svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'
ICON_DL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12m0 0l-5-5m5 5l5-5M4 20h16"/></svg>'
ICON_PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.6-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>'
ICON_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/></svg>'
ICON_SHIELD = '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round" aria-hidden="true"><path d="M32 5l22 8v16c0 14-9.5 25-22 30C19.5 54 10 43 10 29V13z"/><path d="M22 32l7 7 14-15" stroke-linecap="round"/></svg>'


def store_btn(t, cls=""):
    return (f'<a class="btn btn-gold btn-store {cls}" href="{STORE}">{ICON_DL}'
            f'<span class="two"><small>{t["store_small"]}</small><b>{t["store_big"]}</b></span></a>')


def head(t, code, page, title, desc, r, og_image="assets/og-steelhold.jpg", extra=""):
    folder, lang, og_locale, _ = LOCALES[code]
    file = "" if page == "index" else f"{page}.html"
    url = f"{BASE}{folder}{file}"
    alt = ""
    if code in PUBLISHED and page != "press":
        for c in PUBLISHED:
            alt += f'<link rel="alternate" hreflang="{LOCALES[c][1]}" href="{BASE}{LOCALES[c][0]}{file}">\n'
        alt += f'<link rel="alternate" hreflang="x-default" href="{BASE}{file}">\n'
    robots = "" if code in PUBLISHED else '<meta name="robots" content="noindex">\n'
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<meta name="theme-color" content="#0a0d11">
<meta name="color-scheme" content="dark">
<meta name="referrer" content="no-referrer">
<link rel="canonical" href="{url}">
{alt}<meta property="og:type" content="website">
<meta property="og:site_name" content="Steelhold">
<meta property="og:locale" content="{og_locale}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(t['og_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="apple-itunes-app" content="app-id=6780880608">
<link rel="icon" href="{r}favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="{r}icon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="{r}apple-touch-icon.png">
<link rel="manifest" href="{r}site.webmanifest">
<link rel="preload" href="{r}assets/fonts/SairaSemiCondensed-Bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{r}assets/fonts/Tektur-Black.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/site.css">
<script src="{r}assets/site.js" defer></script>
{extra}</head>
<body>
<a class="skip-link" href="#main">{t['skip']}</a>
"""


def header(t, code, page, r):
    press = "press.html" if code == "en" else "../press.html"
    links = [
        ("index.html#game", t["nav_game"], None),
        ("index.html#together", t["nav_together"], None),
        ("index.html#price", t["nav_price"], None),
        ("support.html", t["nav_support"], "support"),
        (press, t["nav_press"], "press"),
    ]
    def items():
        return "".join(
            f'<a href="{h}"{" aria-current=\"page\"" if p == page else ""}>{label}</a>' for h, label, p in links)
    return f"""<header class="site-header">
  <div class="container bar">
    <a class="brand" href="index.html" aria-label="{t['home_aria']}"><img src="{r}assets/img/icon-256.webp" width="34" height="34" alt=""><span>STEELHOLD</span></a>
    <nav class="nav" aria-label="{t['nav_aria']}">{items()}</nav>
    <a class="btn btn-gold btn-sm header-cta" href="{STORE}">{t['store_short']}</a>
    <details class="menu">
      <summary aria-label="{t['nav_menu']}">{ICON_OPEN}{ICON_CLOSE}</summary>
      <nav class="menu-panel" aria-label="{t['nav_aria']}">{items()}{store_btn(t)}</nav>
    </details>
  </div>
</header>
"""


def footer(t, code, page, r):
    press = "press.html" if code == "en" else "../press.html"
    langs = ""
    if code in PUBLISHED and len(PUBLISHED) > 1 and page != "press":
        file = "" if page == "index" else f"{page}.html"
        langs = '<ul class="footer-links" aria-label="Language">' + "".join(
            f'<li><a href="{r}{LOCALES[c][0]}{file or "index.html"}" hreflang="{LOCALES[c][1]}" lang="{LOCALES[c][1]}">{LOCALES[c][3]}</a></li>'
            for c in PUBLISHED) + "</ul>"
    return f"""<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <a class="brand" href="index.html"><img src="{r}assets/img/icon-256.webp" width="34" height="34" alt=""><span>STEELHOLD</span></a>
      <p style="margin:14px 0 0">{t['footer_copy']}</p>
    </div>
    <div>
      <ul class="footer-links">
        <li><a href="support.html">{t['nav_support']}</a></li>
        <li><a href="{press}">{t['nav_press']}</a></li>
        <li><a href="privacy.html">{t['nav_privacy']}</a></li>
        <li><a href="mailto:{MAIL}">{t['nav_contact']}</a></li>
      </ul>
      {langs}
    </div>
    <p class="legal">{t['footer_legal']}</p>
  </div>
</footer>
</body>
</html>
"""


def lang_note(t, code):
    return f'<p class="lang-note">{t["lang_note"]}</p>' if code != "en" else ""


# ---------------------------------------------------------------- index
def page_index(t, code, r):
    side = "(min-width: 900px) 230px, 36vw"
    main = "(min-width: 900px) 290px, 46vw"
    pair = "(min-width: 900px) 270px, 44vw"
    ld = {
        "@context": "https://schema.org", "@type": "SoftwareApplication",
        "name": "Steelhold: Offline Tank Battle", "applicationCategory": "GameApplication",
        "operatingSystem": "iOS, iPadOS, macOS", "url": STORE, "author": {"@type": "Person", "name": "Maxim Frolov"},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "image": BASE + "assets/press/steelhold-icon-1024.png",
    }
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'
    out = head(t, code, "index", t["meta_title"], t["meta_desc"], r, extra=extra) + header(t, code, "index", r)
    chips = "".join(f"<li>{c}</li>" for c in t["chips"])
    stats = "".join(f"<li><b>{n}</b><span>{l}</span></li>" for n, l in t["stats"])
    campaigns = "".join(f"<li><b>{n}</b>{d}</li>" for n, d in t["campaigns"])
    def paras(key):
        return "".join(f"<p>{p}</p>" for p in t[key])
    def points(key):
        return "".join(f"<li>{p}</li>" for p in t[key])
    out += f"""<main id="main">
<section class="hero">
  <div class="container hero-grid">
    <div class="reveal">
      {lang_note(t, code)}<span class="kicker">{t['hero_kicker']}</span>
      <h1 class="title"><span class="word">Steelhold</span><span class="sr-only">: </span><span class="sub">{t['hero_sub']}</span></h1>
      <p class="lead">{t['hero_lead']}</p>
      <ul class="chips">{chips}</ul>
      <div class="ctas">{store_btn(t)}<a class="btn btn-ghost" href="#trailer">{ICON_PLAY}{t['trailer_btn']}</a></div>
    </div>
    <div class="phones" aria-label="{t['hero_shots_aria']}" role="group">
      {phone(r, "boss", t['alt_boss'], side, "side", eager=False)}
      {phone(r, "defend", t['alt_defend'], main, "main", eager=True)}
      {phone(r, "night", t['alt_night'], side, "side")}
    </div>
  </div>
  <div class="container"><ul class="stats">{stats}</ul></div>
</section>

<section class="section" id="game">
  <div class="container split">
    <div class="copy">
      <span class="kicker">{t['f1_kicker']}</span>
      <h2 class="display">{t['f1_title']}</h2>
      {paras('f1_text')}
      <ul class="campaigns">{campaigns}</ul>
    </div>
    <div class="media"><div class="tablet">{pic(r, "ipad", "defend", t['alt_ipad_defend'], "(min-width: 900px) 520px, 92vw")}</div></div>
  </div>
</section>

<section class="section">
  <div class="container split flip">
    <div class="copy">
      <span class="kicker">{t['f2_kicker']}</span>
      <h2 class="display">{t['f2_title']}</h2>
      {paras('f2_text')}
    </div>
    <div class="media phones single">{phone(r, "boss", t['alt_boss'], "(min-width: 900px) 300px, 68vw")}</div>
  </div>
</section>

<section class="section">
  <div class="container split">
    <div class="copy">
      <span class="kicker">{t['f3_kicker']}</span>
      <h2 class="display">{t['f3_title']}</h2>
      {paras('f3_text')}
    </div>
    <div class="media phones pair">{phone(r, "night", t['alt_night'], pair)}{phone(r, "lava", t['alt_lava'], pair)}</div>
  </div>
</section>

<section class="section together" id="together">
  <div class="container split flip">
    <div class="copy">
      <span class="kicker">{t['tg_kicker']}</span>
      <h2 class="display">{t['tg_title']}</h2>
      {paras('tg_text')}
      <ul class="points">{points('tg_points')}</ul>
      <p class="new-box"><span class="tag-new">{t['new_133']}</span> {t['tg_new']}</p>
      <a class="more" href="support.html#play-together">{t['tg_link']}</a>
    </div>
    <div class="media phones pair">{phone(r, "together", t['alt_together'], pair)}{phone(r, "invite", t['alt_invite'], pair)}</div>
  </div>
</section>

<section class="section">
  <div class="container split">
    <div class="copy">
      <span class="kicker">{t['f5_kicker']}</span>
      <h2 class="display">{t['f5_title']}</h2>
      {paras('f5_text')}
    </div>
    <div class="media phones pair">{phone(r, "backup", t['alt_backup'], pair)}{phone(r, "hangar", t['alt_hangar'], pair)}</div>
  </div>
</section>

<section class="section">
  <div class="container split flip">
    <div class="copy">
      <span class="kicker">{t['f6_kicker']}</span>
      <h2 class="display">{t['f6_title']}</h2>
      {paras('f6_text')}
    </div>
    <div class="media phones single">{phone(r, "endless", t['alt_endless'], "(min-width: 900px) 300px, 68vw")}</div>
  </div>
</section>

<section class="section trailer" id="trailer">
  <div class="container split">
    <div class="copy">
      <span class="kicker">{t['tr_kicker']}</span>
      <h2 class="display">{t['tr_title']}</h2>
      {paras('tr_text')}
    </div>
    <div class="media">
      <div class="phone">
        <video controls playsinline preload="none" width="540" height="1170" poster="{r}assets/video/trailer-poster.jpg" aria-label="{t['tr_aria']}">
          <source src="{r}assets/video/steelhold-trailer-iphone.mp4" type="video/mp4">
        </video>
      </div>
    </div>
  </div>
</section>

<section class="section" id="price">
  <div class="container">
    <div class="center-head">
      <span class="kicker">{t['pr_kicker']}</span>
      <h2 class="display">{t['pr_title']}</h2>
    </div>
    <div class="plans">
      <div class="plan">
        <span class="label">{t['pr_free_label']}</span>
        <h3>{t['pr_free_title']}</h3>
        <ul class="points">{points('pr_free_items')}</ul>
      </div>
      <div class="plan full">
        <span class="label">{t['pr_full_label']}</span>
        <h3>{t['pr_full_title']}</h3>
        <ul class="points">{points('pr_full_items')}</ul>
      </div>
    </div>
    <ul class="fair">{points('pr_fair')}</ul>
    <p class="fineprint">{t['pr_note']}</p>
  </div>
</section>

<section class="section" id="devices">
  <div class="container split flip">
    <div class="copy">
      <span class="kicker">{t['dv_kicker']}</span>
      <h2 class="display">{t['dv_title']}</h2>
      {paras('dv_text')}
      <ul class="chips plain">{points('dv_chips')}</ul>
    </div>
    <figure class="media">
      <div class="wide-shot">{pic(r, "duo", "defend", t['alt_duo'], "(min-width: 900px) 560px, 92vw")}</div>
      <figcaption>{t['dv_caption']}</figcaption>
    </figure>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="shield">
      {ICON_SHIELD}
      <div>
        <span class="kicker">{t['pv_kicker']}</span>
        <h2 class="display">{t['pv_title']}</h2>
        {paras('pv_text')}
        <a class="more" href="privacy.html">{t['pv_link']}</a>
      </div>
    </div>
  </div>
</section>

<section class="section final">
  <div class="container">
    <picture><source type="image/webp" srcset="{r}assets/img/icon-256.webp"><img class="app-icon" src="{r}assets/img/icon-256.jpg" width="256" height="256" alt="{t['icon_alt']}" loading="lazy"></picture>
    <h2 class="display">{t['cta_title']}</h2>
    <p class="lead" style="margin:0 auto">{t['cta_text']}</p>
    <div class="ctas">{store_btn(t)}</div>
  </div>
</section>
</main>
"""
    return out + footer(t, code, "index", r)


# ---------------------------------------------------------------- support
def page_support(t, code, r):
    out = head(t, code, "support", t["sp_meta_title"], t["sp_meta_desc"], r) + header(t, code, "support", r)
    quick = "".join(f'<li><a href="#{i}">{label}</a></li>' for i, label in t["sp_quick"])
    groups = ""
    for gid, gtitle, items in t["sp_groups"]:
        qa = "".join(
            f'<details class="qa" id="{qid}"><summary>{q}</summary><div class="answer">{ui(a)}</div></details>\n'
            for qid, q, a in items)
        groups += f'<section class="faq-group" id="{gid}" aria-labelledby="{gid}-h"><h2 id="{gid}-h">{gtitle}</h2>\n{qa}</section>\n'
    out += f"""<main id="main" class="narrow">
<div class="page-hero">
  {lang_note(t, code)}<h1>{t['sp_title']}</h1>
  <p class="lead">{t['sp_lead']}</p>
</div>
<ul class="quick">{quick}</ul>
<p class="dim" style="font-size:15px;margin-top:14px">{ui(t['sp_tabs_note'])}</p>
{groups}
<section class="contact-card" id="contact">
  <h2>{t['sp_contact_title']}</h2>
  <p>{t['sp_contact_text']}</p>
  <a class="btn btn-gold" href="mailto:{MAIL}">{ICON_MAIL}<span>{MAIL}</span></a>
</section>
<div style="height:56px"></div>
</main>
"""
    return out + footer(t, code, "support", r)


# ---------------------------------------------------------------- privacy
def page_privacy(t, code, r):
    out = head(t, code, "privacy", t["pp_meta_title"], t["pp_meta_desc"], r) + header(t, code, "privacy", r)
    secs = "".join(
        f'<section class="doc-section"><h2>{h}</h2>{"".join(f"<p>{p}</p>" for p in ps)}</section>\n'
        for h, ps in t["pp_sections"])
    out += f"""<main id="main" class="narrow">
<div class="page-hero">
  {lang_note(t, code)}<h1>{t['pp_title']}</h1>
  <p class="updated">{t['pp_updated']}</p>
  {f'<p class="dim" style="margin-top:14px">{t["pp_authoritative"]}</p>' if code != "en" else ""}
</div>
{secs}
<div style="height:56px"></div>
</main>
"""
    return out + footer(t, code, "privacy", r)


# ---------------------------------------------------------------- press (English only)
def page_press(t, r=""):
    code = "en"
    out = head(t, code, "press", t["ps_meta_title"], t["ps_meta_desc"], r) + header(t, code, "press", r)
    facts = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in t["ps_facts"])
    timeline = "".join(f"<li><b>{k}</b><br>{v}</li>" for k, v in t["ps_versions"])
    def block(bid, title, paras):
        body = "".join(f"<p>{p}</p>" for p in paras)
        return (f'<div class="copy-block"><div class="copy-bar"><h3>{title}</h3>'
                f'<button class="btn btn-ghost copy-btn" type="button" data-copy="{bid}" data-done="{t["ps_copied"]}" hidden>{t["ps_copy"]}</button></div>'
                f'<div id="{bid}">{body}</div></div>')
    def shots(kind, items, cls):
        cells = ""
        for name, label in items:
            full = f"assets/press/steelhold-{kind}-{name}.jpg"
            size = (ROOT / full).stat().st_size / 1e6 if (ROOT / full).exists() else 0
            stem = name.split("_", 1)[1]
            cells += (f'<li><a href="{full}">{pic(r, kind, stem, label + " (" + t["ps_" + kind] + ")", "(min-width: 1000px) 220px, 45vw")}'
                      f'<span>{label}<i>{size:.1f} MB</i></span></a></li>')
        return f'<ul class="shots {cls}">{cells}</ul>'
    zip_mb = (ROOT / "assets/press/steelhold-press-kit.zip").stat().st_size / 1e6
    out += f"""<main id="main" class="container">
<div class="page-hero">
  <div class="press-head">
    <img src="assets/img/icon-256.webp" width="128" height="128" alt="{t['icon_alt']}">
    <div>
      <h1>{t['ps_title']}</h1>
      <p class="lead">{t['ps_lead']}</p>
    </div>
  </div>
  <div class="dl-row">
    <a class="btn btn-gold" href="assets/press/steelhold-press-kit.zip" download>{ICON_DL}<span>{t['ps_dl_zip']} <small>ZIP · {zip_mb:.0f} MB</small></span></a>
    <a class="btn btn-ghost" href="assets/press/steelhold-icon-1024.png" download>{t['ps_dl_icon']} <small>PNG</small></a>
    <a class="btn btn-ghost" href="assets/video/steelhold-trailer-iphone.mp4" download>{t['ps_dl_video']} <small>MP4 · 4 MB</small></a>
  </div>
</div>

<section class="press-section" id="facts"><h2 class="press-h2">{t['ps_facts_title']}</h2><dl class="facts">{facts}</dl></section>

<section class="press-section split" style="align-items:start">
  <div><h2 class="press-h2">{t['ps_versions_title']}</h2><ul class="timeline">{timeline}</ul></div>
  <div><h2 class="press-h2">{t['ps_diff_title']}</h2><ul class="points diff" style="margin-top:0">{"".join(f"<li>{x}</li>" for x in t['ps_diff'])}</ul></div>
</section>

<section class="press-section" id="text"><h2 class="press-h2">{t['ps_text_title']}</h2>
  <div style="display:grid;gap:16px">
    {block('copy-short', t['ps_short_title'], t['ps_short'])}
    {block('copy-together', t['ps_together_title'], t['ps_together'])}
    {block('copy-long', t['ps_long_title'], t['ps_long'])}
  </div>
</section>

<section class="press-section" id="screenshots"><h2 class="press-h2">{t['ps_shots_title']}</h2>
  <p class="dim">{t['ps_shots_note']}</p>
  <h3 class="kicker" style="margin-top:22px">iPhone · 1320 × 2868</h3>
  {shots('iphone', t['ps_shots'], 'iphone')}
  <h3 class="kicker" style="margin-top:34px">iPad · 2064 × 2752</h3>
  {shots('ipad', t['ps_shots'], 'ipad')}
  <h3 class="kicker" style="margin-top:34px">iPhone Duo · 2853 × 2007</h3>
  <ul class="shots"><li><a href="assets/press/steelhold-iphone-duo-01_defend.jpg">{pic(r, "duo", "defend", t['alt_duo'], "(min-width: 640px) 33vw, 45vw")}<span>{t['ps_duo_label']}<i>{(ROOT / 'assets/press/steelhold-iphone-duo-01_defend.jpg').stat().st_size / 1e6:.1f} MB</i></span></a></li></ul>
</section>

<section class="press-section" id="usage"><h2 class="press-h2">{t['ps_usage_title']}</h2>
  <div class="narrow" style="margin:0">{"".join(f'<p class="dim">{p}</p>' for p in t['ps_usage'])}</div>
  <a class="btn btn-gold" href="mailto:{MAIL}">{ICON_MAIL}<span style="text-transform:none;letter-spacing:.02em">{MAIL}</span></a>
</section>
<div style="height:64px"></div>
</main>
"""
    return out + footer(t, code, "press", r)


def main():
    en = load("en")
    written = []
    for code, (folder, *_rest) in LOCALES.items():
        t = dict(en)
        if code != "en":
            if not (ROOT / "tools" / "locales" / f"{code.replace('-', '_')}.py").exists():
                continue
            t.update(load(code))
        r = "" if code == "en" else "../"
        outdir = ROOT / folder
        outdir.mkdir(exist_ok=True)
        for page, fn in (("index", page_index), ("support", page_support), ("privacy", page_privacy)):
            (outdir / f"{page}.html").write_text(fn(t, code, r), encoding="utf-8")
            written.append(f"{folder}{page}.html")
    (ROOT / "press.html").write_text(page_press(en), encoding="utf-8")
    written.append("press.html")
    print("\n".join(written))


if __name__ == "__main__":
    main()
