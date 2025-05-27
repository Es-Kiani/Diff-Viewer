from flask import Flask, render_template_string, request, session
import difflib, json, PyPDF2, importlib
from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter

app = Flask(__name__)
app.secret_key = 'innovation_diff_tool_secret'

# پشتیبانی از docx
try:
    docx_module = importlib.import_module('docx')
    Document = getattr(docx_module, 'Document', None)
    if Document is None:
        raise ImportError
    docx_supported = True
except ImportError:
    Document = None
    docx_supported = False

formatter = HtmlFormatter(cssclass='highlight', nowrap=True)
pygments_css = formatter.get_style_defs('.highlight')

CODE_LANG_MAP = {
    'py': 'python', 'js': 'javascript', 'cpp': 'cpp',
    'java': 'java', 'ipynb': 'python'
}

STYLE = f'''
<style>
body {{ font-family: 'Rubik', sans-serif; background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%); margin: 0; padding: 20px; }}
h2 {{ text-align: center; color: #333; }}
form {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 6px 24px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 15px; }}
.code-box {{ background: #fff; border: 1px solid #ccc; border-radius: 8px; padding: 15px; height: 400px; overflow-y: scroll; white-space: pre-wrap; font-family: monospace; }}
.diff-table {{ display: flex; gap: 20px; max-width: 95%; margin: 30px auto; }}
.line-number {{ display: inline-block; width: 2em; text-align: right; margin-right: 0.5em; color: #888; }}
.line-symbol {{ display: inline-block; width: 1em; margin-right: 0.5em; }}
.added-line {{ background-color: #e6ffe6; }}
.removed-line {{ background-color: #ffe6e6; }}
a.home-link {{ display:block; text-align:center; font-weight:bold; text-decoration:none; margin-bottom:20px; color:#185a9d; }}
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {{
  const left = document.getElementById('leftPane');
  const right = document.getElementById('rightPane');
  if (left && right) {{
    left.onscroll = () => right.scrollTop = left.scrollTop;
    right.onscroll = () => left.scrollTop = right.scrollTop;
  }}
}});
</script>
<style>{pygments_css}</style>
'''

HOME = '''<html><head><title>Diff Tool</title><style>@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;600&display=swap');body{font-family:'Rubik',sans-serif;background:linear-gradient(to right,#ffecd2,#fcb69f);display:flex;align-items:center;justify-content:center;height:100vh;margin:0}.card{background:white;border-radius:20px;box-shadow:0 12px 30px rgba(0,0,0,0.15);padding:50px 60px;text-align:center;animation:fadeIn 1s ease-in-out;max-width:400px;width:90%}h1{font-size:26px;color:#333;margin-bottom:30px}.mode-btn{display:block;width:100%;padding:15px 0;margin:10px 0;font-size:18px;font-weight:600;color:white;background:linear-gradient(to right,#667eea,#764ba2);border:none;border-radius:12px;cursor:pointer;transition:.3s}.mode-btn:hover{transform:translateY(-3px);box-shadow:0 10px 20px rgba(0,0,0,0.2)}.footer{margin-top:30px;font-size:14px;color:#666}@keyframes fadeIn{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}</style></head><body><div class="card"><h1>Select Comparison Mode</h1><form action="/upload-mode"><button class="mode-btn">🔍 Compare Files</button></form><form action="/text-mode"><button class="mode-btn">✍️ Compare Text</button></form><div class="footer">Crafted with ❤️ by Innovation</div></div></body></html>'''
UPLOAD = '''<html><head><title>Upload</title>{{ style|safe }}</head><body>
<a href="/" class="home-link">← Back to Home</a>
<h2>Upload Two Files to Compare</h2>
<form method="post" enctype="multipart/form-data">
<input type="file" name="file1" required>
<input type="file" name="file2" required>
<label><input type="checkbox" name="diff_only" onchange="this.form.submit();" {{ 'checked' if diff_only }}> Diff-only Mode</label>
<button type="submit">Compare</button>
</form>
{% if similarity is not none %}<p style="text-align:center">Similarity Score: {{ (similarity * 100) | round(2) }}%</p>{% endif %}
{% if file_type_error %}<p style="color:red;text-align:center">Error: Files must be the same type</p>{% endif %}
{% if rendered_old and rendered_new %}
<div class="diff-table">
  <div class="code-box" id="leftPane">{{ rendered_old|safe }}</div>
  <div class="code-box" id="rightPane">{{ rendered_new|safe }}</div>
</div>
{% endif %}
</body></html>'''

TEXT = '''<html><head><title>Text Compare</title>{{ style|safe }}</head><body>
<a href="/" class="home-link">← Back to Home</a>
<h2>Compare Text</h2>
<form method="post">
<textarea name="old_text" rows="10" placeholder="Old text...">{{ old_text or '' }}</textarea>
<textarea name="new_text" rows="10" placeholder="New text...">{{ new_text or '' }}</textarea>
<label><input type="checkbox" name="diff_only" onchange="this.form.submit();" {{ 'checked' if diff_only }}> Diff-only Mode</label>
<button type="submit">Compare</button>
</form>
{% if similarity is not none %}<p style="text-align:center">Similarity Score: {{ (similarity * 100) | round(2) }}%</p>{% endif %}
{% if rendered_old and rendered_new %}
<div class="diff-table">
  <div class="code-box" id="leftPane">{{ rendered_old|safe }}</div>
  <div class="code-box" id="rightPane">{{ rendered_new|safe }}</div>
</div>
{% endif %}
</body></html>'''

def escape_html(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def extract_code_cells(nb):
    return [line for c in nb.get('cells', []) if c.get('cell_type') == 'code' for line in c.get('source', []) if line.strip()]

def smart_extract(fs):
    ext = fs.filename.rsplit('.', 1)[-1].lower()
    if ext == 'ipynb':
        try:
            code = extract_code_cells(json.load(fs.stream))
            return code, 'Notebook', 'python'
        except:
            pass
    if ext in CODE_LANG_MAP:
        fs.stream.seek(0)
        return fs.stream.read().decode('utf-8', 'ignore').splitlines(), 'Text', CODE_LANG_MAP[ext]
    if ext == 'docx':
        if docx_supported and Document:
            return [p.text for p in Document(fs.stream).paragraphs], 'Text', 'word'
        fs.stream.seek(0)
        return fs.stream.read().decode('utf-8', 'ignore').splitlines(), 'Text', 'word'
    if ext == 'pdf':
        return [l for p in PyPDF2.PdfReader(fs.stream).pages for l in (p.extract_text() or '').splitlines()], 'Text', 'pdf'
    fs.stream.seek(0)
    return fs.stream.read().decode('utf-8', 'ignore').splitlines(), 'Text', 'text'
def generate_diff_output(old, new, diff_only, lang):
    l, r = [], []
    seq = difflib.SequenceMatcher(None, old, new)
    for tag, i1, i2, j1, j2 in seq.get_opcodes():
        if diff_only and tag == 'equal':
            continue
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

@app.route('/')
def home():
    return HOME

@app.route('/upload-mode', methods=['GET', 'POST'])
def upload_mode():
    diff_only = 'diff_only' in request.form or 'diff_only' in request.args
    session['diff_only'] = diff_only
    similarity = None
    rendered_old = rendered_new = ''
    file_type_error = False
    if request.method == 'POST':
        f1 = request.files.get('file1')
        f2 = request.files.get('file2')
        if not f1 or not f2:
            return 'Please upload two files.'
        c1, t1, l1 = smart_extract(f1)
        f1.stream.seek(0)
        c2, t2, l2 = smart_extract(f2)
        f2.stream.seek(0)
        if t1 != t2:
            file_type_error = True
        else:
            similarity = difflib.SequenceMatcher(None, "\n".join(c1), "\n".join(c2)).ratio()
            rendered_old, rendered_new = generate_diff_output(c1, c2, diff_only, l1)
    return render_template_string(UPLOAD, style=STYLE,
        diff_only=session.get('diff_only', False),
        similarity=similarity, rendered_old=rendered_old,
        rendered_new=rendered_new, file_type_error=file_type_error)
@app.route('/text-mode', methods=['GET', 'POST'])
def text_mode():
    old_text = new_text = ''
    diff_only = 'diff_only' in request.form or 'diff_only' in request.args
    session['diff_only'] = diff_only
    similarity = None
    rendered_old = rendered_new = ''
    if request.method == 'POST':
        old_text = request.form.get('old_text', '')
        new_text = request.form.get('new_text', '')
        similarity = difflib.SequenceMatcher(None, old_text, new_text).ratio()
        rendered_old, rendered_new = generate_diff_output(
            old_text.splitlines(), new_text.splitlines(), diff_only, 'text')
    return render_template_string(TEXT, style=STYLE,
        old_text=old_text, new_text=new_text,
        diff_only=session.get('diff_only', False),
        similarity=similarity,
        rendered_old=rendered_old, rendered_new=rendered_new)

if __name__ == '__main__':
    app.run(debug=True)
