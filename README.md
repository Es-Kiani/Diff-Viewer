# 🧠 Diff Tool — File & Text Comparison Web App

A modern and beautiful web-based application for comparing files and plain texts with side-by-side diff visualization, syntax highlighting, and support for PDF, Word, code files, and Jupyter notebooks.

---

## 🚀 Features

- 📂 Compare any two text/code files: `.py`, `.js`, `.cpp`, `.java`, `.ipynb`, `.pdf`, `.docx`, and more.
- ✍️ Or just paste two texts directly and compare them line by line.
- 🎨 Syntax highlighting (via Pygments) for all supported code formats.
- 🔍 Diff-only mode to view only modified/added/removed lines.
- 🧾 Shows line numbers, change markers, and color-coded diffs.
- 🔄 Scroll-sync between both sides.
- 🌐 Minimal Flask app with no frontend dependencies.

---

## 📁 Project Structure

```
diff_tool/
├── app.py                 # Flask app entry point
├── templates.py           # HTML templates
├── styles.py              # CSS and JS block
├── requirements.txt
└── logic/
    ├── __init__.py
    ├── utils.py           # HTML escaping, etc.
    ├── file_loader.py     # Loads files of different formats
    └── diff_engine.py     # Core diff comparison engine
```

---

## ▶️ How to Run

```bash
git clone https://github.com/your-username/diff_tool.git
cd diff_tool
pip install -r requirements.txt
python app.py
```

Then open your browser at:  
👉 http://127.0.0.1:5000

---

## 📦 Requirements

- Python 3.7+
- Flask
- PyPDF2
- Pygments
- python-docx

Install via:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

This project is licensed under the MIT License.

---