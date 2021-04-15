from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/botanic.html")
def botanic():
    return render_template('botanic.html')

@app.route("/navitas.html")
def navitas():
    return render_template('navitas.html')

@app.route("/miniCsharp.html")
def mini_csharp():
    return render_template('miniCsharp.html')

@app.route("/client-server.html")
def client_server():
    return render_template('client-server.html')



if __name__ == "__main__":
    app.run(debug=True, port=5000)