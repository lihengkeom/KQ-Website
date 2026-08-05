import os
import sys
from html.parser import HTMLParser

class ImgSrcParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.srcs = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'img':
            attrs = dict(attrs)
            if 'src' in attrs:
                self.srcs.append(attrs['src'])

root = os.path.dirname(__file__)
html_path = os.path.join(root, 'product.html')
if not os.path.exists(html_path):
    print('product.html not found')
    sys.exit(1)

with open(html_path, 'r', encoding='utf-8') as f:
    data = f.read()

parser = ImgSrcParser()
parser.feed(data)

missing = []
print('Checking', len(parser.srcs), 'image src entries...')
for src in parser.srcs:
    # normalize possible leading slashes
    src_path = src.lstrip('/')
    full_path = os.path.join(root, src_path)
    if os.path.exists(full_path):
        print('[OK] ', src)
        continue
    # try case-insensitive search within the same directory
    dirpart = os.path.dirname(full_path) or root
    namepart = os.path.basename(full_path)
    found_case = None
    if os.path.isdir(dirpart):
        for fn in os.listdir(dirpart):
            if fn.lower() == namepart.lower():
                found_case = os.path.join(dirpart, fn)
                break
    # try replacing %2B or %2b with + and vice versa
    alt_candidates = []
    if '%2B' in src or '%2b' in src:
        alt_candidates.append(src.replace('%2B','+').replace('%2b','+'))
    if '+' in src:
        alt_candidates.append(src.replace('+','%2B'))
    # try replacing plus with dash
    if '+' in src:
        alt_candidates.append(src.replace('+','-'))
    suggestion = None
    for alt in alt_candidates:
        alt_path = os.path.join(root, alt.lstrip('/'))
        if os.path.exists(alt_path):
            suggestion = alt
            break
    if found_case:
        print('[CASE MISMATCH] ', src, '->', os.path.relpath(found_case, root))
        missing.append((src, 'case', os.path.relpath(found_case, root)))
    elif suggestion:
        print('[ALT FOUND] ', src, '->', suggestion)
        missing.append((src, 'alt', suggestion))
    else:
        print('[MISSING] ', src)
        missing.append((src, 'missing', None))

print('\nSummary:')
print('  Total referenced:', len(parser.srcs))
print('  Missing / mismatched:', len(missing))
for m in missing:
    print('   -', m)

if len(missing) == 0:
    print('\nAll images present on disk.')
else:
    print('\nSuggestions:')
    print(' - Rename files on server to match casing used in `product.html` (Linux hosts are case-sensitive).')
    print(" - Replace '+' in filenames with '-' or '_' and update `product.html` accordingly.")
    print(' - Avoid non-ASCII directory names or ensure they were uploaded and URL-encoded correctly.')
