#!/usr/bin/env python3
"""Generate cards/<name>-{dark,light}.svg and the README project section from projects.json.

Usage: python3 scripts/build-cards.py   (stdlib only; run from anywhere)
Static SVGs: system fonts only, no scripts, no foreignObject.
README: the block between <!-- projects:start --> and <!-- projects:end --> is rewritten.
"""
import colorsys, json, pathlib, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
THEMES = {
    "dark": {"bg": "#0d1117", "ink": "#e6edf3", "muted": "#9199a5", "edge": "#30363d"},
    "light": {"bg": "#ffffff", "ink": "#1f2328", "muted": "#59636e", "edge": "#d1d9e0"},
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
GLYPHS = {
    "page": '<path d="M20 50 V14 H38 L46 22 V50" {s}/><circle cx="38" cy="22" r="3.8" fill="{a}"/>',
    "gauge": '<path d="M14 44 A18 18 0 0 1 50 44" {s}/><path d="M32 44 L40 30" {s}/><circle cx="32" cy="44" r="4.2" fill="{a}"/>',
    "brackets": '<path d="M24 20 L14 32 L24 44 M40 20 L50 32 L40 44" {s}/><circle cx="32" cy="32" r="3.8" fill="{a}"/>',
    "lens": '<path d="M38 38 L50 50" {s}/><path d="M28 14 A14 14 0 1 0 28.01 14" {s}/><circle cx="28" cy="28" r="3.8" fill="{a}"/>',
    "shield": '<path d="M32 52 C21 46 16 38 16 22 L32 14 L48 22 C48 38 43 46 32 52" {s}/><circle cx="32" cy="32" r="3.8" fill="{a}"/>',
    "chart": '<path d="M12 46 L24 34 L34 40 L50 20" {s}/><circle cx="50" cy="20" r="4.2" fill="{a}"/>',
}


def accent_for(hexcolor, theme):
    if theme == "dark":
        return hexcolor
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, 0.45, min(s, 0.5))
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(p, theme):
    c, a = THEMES[theme], accent_for(p["accent"], theme)
    stroke = f'fill="none" stroke="{c["ink"]}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"'
    glyph = GLYPHS[p["glyph"]].format(s=stroke, a=a)
    lines = textwrap.wrap(p["text"], 44)[:2]
    body = "".join(
        f'<text x="16" y="{78 + i * 18}" font-family="{SANS}" font-size="13" fill="{c["muted"]}">{esc(t)}</text>'
        for i, t in enumerate(lines)
    )
    chips = "".join(
        f'<rect x="{16 + i * 92}" y="118" width="84" height="20" rx="5" fill="none" stroke="{c["edge"]}"/>'
        f'<text x="{58 + i * 92}" y="132" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{c["muted"]}">{esc(t)}</text>'
        for i, t in enumerate(p["chips"])
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="150" viewBox="0 0 320 150" role="img" '
        f'aria-label="{esc(p["name"])}: {esc(p["text"])}">'
        f'<rect x=".5" y=".5" width="319" height="149" rx="12" fill="{c["bg"]}" stroke="{c["edge"]}"/>'
        f'<path d="M12 .5 H308 A12 12 0 0 1 320 12.5 V13 H0 V12.5 A12 12 0 0 1 12 .5Z" fill="{a}"/>'
        f'<svg x="16" y="26" width="34" height="34" viewBox="0 0 64 64">{glyph}</svg>'
        f'<text x="58" y="50" font-family="{SANS}" font-weight="800" font-size="19" letter-spacing="-.5" fill="{c["ink"]}">'
        f'{esc(p["name"])}<tspan fill="{a}">.</tspan></text>{body}{chips}</svg>\n'
    )


def main():
    data = json.loads((ROOT / "projects.json").read_text())
    (ROOT / "cards").mkdir(exist_ok=True)
    md = []
    for g in data["groups"]:
        md.append(f"<sub><b>{g['title']}</b></sub>\n<p>")
        for p in g["projects"]:
            for theme in THEMES:
                (ROOT / "cards" / f"{p['name']}-{theme}.svg").write_text(card(p, theme))
            md.append(
                f'<a href="https://github.com/{data["owner"]}/{p["name"]}"><picture>'
                f'<source media="(prefers-color-scheme: dark)" srcset="cards/{p["name"]}-dark.svg">'
                f'<img src="cards/{p["name"]}-light.svg" width="320" alt="{p["name"]}: {esc(p["text"])}"></picture></a>'
            )
        md.append("</p>\n")
    block = "<!-- projects:start -->\n" + "\n".join(md) + "<!-- projects:end -->"
    readme = ROOT / "README.md"
    text = readme.read_text()
    a, b = text.index("<!-- projects:start -->"), text.index("<!-- projects:end -->") + len("<!-- projects:end -->")
    readme.write_text(text[:a] + block + text[b:])


if __name__ == "__main__":
    main()
