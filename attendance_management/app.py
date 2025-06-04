from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True, port=5003) # Running on a different port
