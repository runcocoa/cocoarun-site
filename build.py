#!/usr/bin/env python3
"""Builds the Cocoa Run website from the listing chat's page drafts.

Run: python3 build.py
Reads ~/Documents/cocoa-run-assets/2026-09-24-app-store-listing/pages/*.md
Writes index.html, privacy/, terms/, support/, 404.html and app-ads.txt here.
"""
import html
import os
import re
import sys

DRAFTS = os.path.expanduser('~/Documents/cocoa-run-assets/2026-09-24-app-store-listing/pages')
HERE = os.path.dirname(os.path.abspath(__file__))

EFFECTIVE_DATE = '24 September 2026'
RETENTION_CRASH = 'no longer than 90 days'
BANNED = [chr(c) for c in (0x2014, 0x2013, 0x2192, 0x2022, 0xB7)]

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/fonts.css">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="top">
<a class="brand" href="/">Cocoa Run</a>
<nav aria-label="Main">
<a href="/support/"{s_cur}>Support</a>
<a href="/privacy/"{p_cur}>Privacy</a>
<a href="/terms/"{t_cur}>Terms</a>
</nav>
</header>
'''

FOOT = '''<footer class="foot">
<p>Cocoa Run is made by Gettmi Inc. Limited.</p>
<p><a href="mailto:info@gettmi.com">info@gettmi.com</a></p>
</footer>
</body>
</html>
'''


def head(title, desc, current=''):
    cur = ' aria-current="page"'
    return HEAD.format(title=html.escape(title), desc=html.escape(desc),
                       s_cur=cur if current == 'support' else '',
                       p_cur=cur if current == 'privacy' else '',
                       t_cur=cur if current == 'terms' else '')


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(https?://[^\s<)]+)', r'<a href="\1">\1</a>', text)
    text = re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+)', r'<a href="mailto:\1">\1</a>', text)
    return text


def md_to_html(md):
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S).strip()
    out, para, items = [], [], []

    def flush():
        if para:
            out.append('<p>' + '<br>'.join(inline(l) for l in para) + '</p>')
            para.clear()
        if items:
            out.append('<ul>' + ''.join('<li>' + inline(i) + '</li>' for i in items) + '</ul>')
            items.clear()

    for line in md.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith('# '):
            flush(); out.append('<h1>' + inline(s[2:]) + '</h1>')
        elif s.startswith('## '):
            flush(); out.append('<h2>' + inline(s[3:]) + '</h2>')
        elif s.startswith('- '):
            if para:
                flush()
            items.append(s[2:])
        else:
            if items:
                flush()
            para.append(s)
    flush()
    return '\n'.join(out)


def draft(name):
    with open(os.path.join(DRAFTS, name + '.md')) as f:
        return f.read()


def write(rel, text):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(text)


def doc_page(slug, name, title, desc, fixes):
    md = re.sub(r'<!--.*?-->', '', draft(name), flags=re.S)
    for a, b in fixes:
        md = md.replace(a, b)
    left = re.findall(r'\{[A-Z_]+\}', md)
    if left:
        sys.exit(f'{name}: placeholders left: {left}')
    body = '<main class="doc">\n' + md_to_html(md) + '\n</main>\n'
    write(f'{slug}/index.html', head(title, desc, slug) + body + FOOT)


def main():
    doc_page('privacy', 'privacy-policy', 'Cocoa Run Privacy Policy',
             'What Cocoa Run collects, why, and what you can do about it.',
             [('{EFFECTIVE_DATE}', EFFECTIVE_DATE), ('{RETENTION_CRASH}', RETENTION_CRASH)])

    terms = draft('terms-of-use')
    law = re.search(r'\n## Law\n.*?(?=\n## |\Z)', terms, re.S)
    doc_page('terms', 'terms-of-use', 'Cocoa Run Terms of Use',
             'The terms for playing Cocoa Run.',
             [('{EFFECTIVE_DATE}', EFFECTIVE_DATE)] + ([(law.group(0), '')] if law else []))

    doc_page('support', 'support', 'Cocoa Run Support',
             'Help with runs, Hot Shots, plans, purchases and your account.',
             [('Privacy Policy: {SITE_URL}/privacy', 'Privacy Policy: /privacy/'),
              ('Terms of Use: {SITE_URL}/terms', 'Terms of Use: /terms/')])
    # The two lines above become plain text; make them links.
    p = os.path.join(HERE, 'support/index.html')
    s = open(p).read()
    s = s.replace('Privacy Policy: /privacy/', '<a href="/privacy/">Privacy Policy</a>')
    s = s.replace('Terms of Use: /terms/', '<a href="/terms/">Terms of Use</a>')
    open(p, 'w').write(s)

    home = head('Cocoa Run: beat the clock for gold',
                'Chase Zack\'s train up 8 mountains, beat the clock on 40 levels and win gold before the cocoa goes cold. For iPhone.') + '''<main>
<section class="hero">
<div class="hero-text">
<p class="eyebrow">For iPhone</p>
<h1>Beat the clock for gold</h1>
<p class="lead">Zack left his hot cocoa behind. Chase his train up 8 mountains, beat the clock on 40 levels and win gold before the cocoa goes cold.</p>
<p class="soon">Coming soon to the App Store</p>
</div>
<img class="hero-art" src="/assets/monty-wave.png" width="504" height="560" alt="Monty the fox in orange goggles and a blue scarf, waving">
</section>
<section class="band">
<ul class="cards">
<li><h2>5 sports</h2><p>Kayak, skateboard, figure skating, ski and paraglide, one mountain at a time.</p></li>
<li><h2>Hot Shots</h2><p>Fire one just after a perfect gate and it becomes a Perfect Shot.</p></li>
<li><h2>Race yourself</h2><p>Your best run comes back as a ghost, so every attempt is a race.</p></li>
</ul>
</section>
<section class="summit">
<img src="/assets/treehouse.png" width="1100" height="903" alt="Zack's treehouse built into a giant pine at the top of the mountain, with a spiral stair, a tube slide and a red train at its station">
<div>
<h2>The last stop is Zack's treehouse</h2>
<p>Every mountain gets you closer. Deliver the cocoa while it is still piping hot.</p>
</div>
</section>
<section class="facts">
<p>Free to play, with optional plans and in-app purchases. For ages 13 and over, in the United States.</p>
</section>
</main>
''' + FOOT
    write('index.html', home)

    write('404.html', head('Page not found: Cocoa Run', 'This page does not exist.') +
          '<main class="doc"><h1>This page took a wrong turn</h1><p><a href="/">Back to Cocoa Run</a></p></main>\n' + FOOT)
    with open(os.path.join(DRAFTS, 'app-ads.txt')) as f:
        write('app-ads.txt', f.read().strip() + '\n')
    write('robots.txt', 'User-agent: *\nAllow: /\n')
    write('.nojekyll', '')

    bad = 0
    for root, _, files in os.walk(HERE):
        if '.git' in root:
            continue
        for fn in files:
            if fn.endswith(('.html', '.css', '.txt')) and not fn.startswith('OFL'):
                t = open(os.path.join(root, fn)).read()
                hits = sum(t.count(b) for b in BANNED)
                if hits:
                    print('banned characters in', fn, hits); bad += hits
    print('built; banned characters:', bad)


if __name__ == '__main__':
    main()
