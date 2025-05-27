from flask import Flask
from views import configure_routes

app = Flask(__name__)
app.secret_key = 'innovation_diff_tool_secret'

configure_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
