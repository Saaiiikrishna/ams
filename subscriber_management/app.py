from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True, port=5002) # Running on a different port
