import difflib
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

formatter = HtmlFormatter(cssclass='highlight', nowrap=True)

def generate_diff_output(old, new, diff_only, lang):
    l, r = [], []
    seq = difflib.SequenceMatcher(None, old, new)
    for tag, i1, i2, j1, j2 in seq.get_opcodes():
        if diff_only and tag == 'equal': continue
        for k in range(max(i2 - i1, j2 - j1)):
            left_line = old[i1 + k] if k < i2 - i1 else ''
            right_line = new[j1 + k] if k < j2 - j1 else ''
            lineno = i1 + k + 1 if k < i2 - i1 else ''
            symbol = '-' if tag == 'delete' else '+' if tag == 'insert' else '~'
            num = f"<span class='line-number'>{lineno}</span>"
            sym = f"<span class='line-symbol'>{symbol}</span>"
            left_content = highlight(left_line, get_lexer_by_name(lang), formatter) if left_line else ''
            right_content = highlight(right_line, get_lexer_by_name(lang), formatter) if right_line else ''
            left_class = 'removed-line' if tag in ('delete', 'replace') else ''
            right_class = 'added-line' if tag in ('insert', 'replace') else ''
            l.append(f"<div class='{left_class}'>{num}{sym}{left_content}</div>")
            r.append(f"<div class='{right_class}'>{num}{sym}{right_content}</div>")
    return ''.join(l), ''.join(r)
