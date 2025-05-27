HOME = '''<html><head><title>Diff Tool</title><style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;600&display=swap');
body {
    font-family: 'Rubik', sans-serif;
    background: linear-gradient(to right,#ffecd2,#fcb69f);
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    margin: 0;
}
.card {
    background: white;
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    padding: 50px 60px;
    text-align: center;
    animation: fadeIn 1s ease-in-out;
    max-width: 400px;
    width: 90%;
}
h1 {
    font-size: 26px;
    color: #333;
    margin-bottom: 30px;
}
.mode-btn {
    display: block;
    width: 100%;
    padding: 15px 0;
    margin: 10px 0;
    font-size: 18px;
    font-weight: 600;
    color: white;
    background: linear-gradient(to right,#667eea,#764ba2);
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: .3s;
}
.mode-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
.footer {
    margin-top: 30px;
    font-size: 14px;
    color: #666;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style></head>
<body>
<div class="card">
<h1>Select Comparison Mode</h1>
<form action="/upload-mode"><button class="mode-btn">🔍 Compare Files</button></form>
<form action="/text-mode"><button class="mode-btn">✍️ Compare Text</button></form>
<div class="footer">Crafted with ❤️ by Stephen</div>
</div>
</body></html>'''

UPLOAD = '''<html><head><title>Upload</title>{{ style|safe }}</head><body>
<a href="/" class="home-link">← Back to Home</a>
<h2>Upload Two Files to Compare</h2>
<form method="post" enctype="multipart/form-data">
<input type="file" name="file1" required>
<input type="file" name="file2" required>
<label><input type="checkbox" name="diff_only" onchange="this.form.submit();" {{ 'checked' if diff_only }}> Diff-only Mode</label>
<button type="submit">Compare</button>
</form>
{% if similarity is not none %}
<p style="text-align:center">Similarity Score: {{ (similarity * 100) | round(2) }}%</p>
{% endif %}
{% if file_type_error %}
<p style="color:red;text-align:center">Error: Files must be the same type</p>
{% endif %}
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
{% if similarity is not none %}
<p style="text-align:center">Similarity Score: {{ (similarity * 100) | round(2) }}%</p>
{% endif %}
{% if rendered_old and rendered_new %}
<div class="diff-table">
  <div class="code-box" id="leftPane">{{ rendered_old|safe }}</div>
  <div class="code-box" id="rightPane">{{ rendered_new|safe }}</div>
</div>
{% endif %}
</body></html>'''
