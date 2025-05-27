from flask import render_template_string, request, session
import difflib

from templates import HOME, UPLOAD, TEXT
from styles import STYLE
from file_loader import smart_extract
from diff_engine import generate_diff_output

def configure_routes(app):
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
            c1, t1, l1 = smart_extract(f1); f1.stream.seek(0)
            c2, t2, l2 = smart_extract(f2); f2.stream.seek(0)
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
            similarity=similarity, rendered_old=rendered_old,
            rendered_new=rendered_new)
