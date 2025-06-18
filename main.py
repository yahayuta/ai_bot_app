import os

from flask import Flask  # type: ignore # Flask web framework

from handle_line import line_app  # LINE messaging API handler blueprint
from handle_facebook import facebook_app  # Facebook Messenger API handler blueprint

# Create the main Flask application
app = Flask(__name__)
# Register the LINE and Facebook blueprints to handle their respective routes
app.register_blueprint(line_app)
app.register_blueprint(facebook_app)

if __name__ == "__main__":
    # Run the Flask app in debug mode, listening on all interfaces and configurable port
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
