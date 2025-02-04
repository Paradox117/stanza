from flask import Flask, render_template
from views import views
from datetime import timedelta
import os

app = Flask(__name__)
app.register_blueprint(views)
app.permanent_session_lifetime = timedelta(days=7)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html", name=404), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
