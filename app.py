import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def opendb():
    connection = sqlite3.connect("sistema_chamados.db")
    connection.row_factory = sqlite3.Row
    return connection

def closedb(connection):
    connection.close()

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        if not email or not senha:
            return redirect("/")
        db = opendb()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE email = ? AND senha = ?",(email, senha))
        id = cursor.fetchone()
        if not id:
            return redirect("/")
        else:
            print("okay")
            dados = cursor.execute("SELECT status FROM chamados WHERE usuario_id = ?",(id))
            return render_template("dashboard.html")

    
    return render_template("index.html")

@app.route("/dashboard", methods = ["POST"])
def dashboard():
    if request.method == "POST":
        return render_template("dashboard.html")

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar")
        if not email or not senha or not confirmar:
            return redirect("/")
        elif senha != confirmar:
            return redirect("/")
        db = opendb()
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (email, password, confirm_pass) values(?,?,?)", (email, senha, confirmar))
        db.commit()
        closedb(db)
        return redirect("/")
    return render_template("cadastrar.html")

@app.route("/chamados")
def chamados():
    return render_template("chamados.html")

@app.route("/clientes")
def clientes():
    return render_template("clientes.html")

@app.route("/cadastrar_clientes")
def cadClientes():
    return render_template("cadastrar_clientes.html")

@app.route("/cadastrar_chamados")
def cadChamados():
    return render_template("cadastrar_chamados.html")



if __name__ == "__main__":
    app.run(debug=True)






