import os

from flask import Flask
from handle_line import line_app
from handle_facebook import facebook_app

app = Flask(__name__)
app.register_blueprint(line_app)
app.register_blueprint(facebook_app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
