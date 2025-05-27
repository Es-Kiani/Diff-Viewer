from pygments.formatters import HtmlFormatter

formatter = HtmlFormatter(cssclass='highlight', nowrap=True)
pygments_css = formatter.get_style_defs('.highlight')

STYLE = f"""
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
"""
