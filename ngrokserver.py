from flask import Flask, Response, request  # <-- IMPORTAR request

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def home():
    if request.method == "HEAD":  # <-- usar 'request', no 'Flask.request'
        return Response(status=200)

    # GET normal
    return "OK"

if __name__ == "__main__":
    app.run(port=50000)
