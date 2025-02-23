from flask import Flask
from routes import create_routes

app = Flask(__name__)
create_routes(app)

# 🔹 Start the Flask app on port 5002
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
