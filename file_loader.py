import json, PyPDF2, importlib

try:
    docx_module = importlib.import_module('docx')
    Document = getattr(docx_module, 'Document', None)
    docx_supported = True
except ImportError:
    Document = None
    docx_supported = False

CODE_LANG_MAP = {
    'py': 'python', 'js': 'javascript', 'cpp': 'cpp',
    'java': 'java', 'ipynb': 'python'
}

def extract_code_cells(nb):
    return [line for c in nb.get('cells', []) if c.get('cell_type') == 'code' for line in c.get('source', []) if line.strip()]

def smart_extract(fs):
    ext = fs.filename.rsplit('.', 1)[-1].lower()
    if ext == 'ipynb':
        try:
            return extract_code_cells(json.load(fs.stream)), 'Notebook', 'python'
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
