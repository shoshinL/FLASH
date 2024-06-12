import os
import signal
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

PID = os.getpid()
app = Flask(__name__)
app_config = {"host": "0.0.0.0", "port": sys.argv[1]}

"""
---------------------- DEVELOPER MODE CONFIG -----------------------
"""
# Developer mode uses app.py
if "app.py" in sys.argv[0]:
  # Update app config
  app_config["debug"] = True

  # CORS settings
  cors = CORS(
    app,
    resources={r"/*": {"origins": "http://localhost*"}},
  )

  # CORS headers
  app.config["CORS_HEADERS"] = "Content-Type"


"""
--------------------------- REST CALLS -----------------------------
"""
# Remove and replace with your own
@app.route("/example")
def example():

  # See /src/components/App.js for frontend call
  return jsonify(f"Example response from Flask! Learn more in /app.py & /src/components/App.js\nI'm writing even more! Name: {__name__}")


"""
-------------------------- APP SERVICES ----------------------------
"""
# Quits Flask on Electron exit
@app.route('/quit')
def quit():
    # Function to shut down the server
    pid = os.getpid()
    assert pid == PID 
    os.kill(pid, signal.SIGINT)

    return 'Server shutting down...', 200


if __name__ == "__main__":
  app.run(**app_config)
