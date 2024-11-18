import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

USER = 1

def opendb():
    connection = sqlite3.connect("sistema_chamados.db")
    connection.row_factory = sqlite3.Row
    return connection

def closedb(connection):
    connection.close()

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
        return render_template("login.html")


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar")
        if not email or not senha or not confirmar:
            return redirect("/cadastrar")
        elif senha != confirmar:
            return redirect("/cadastrar")
        db = opendb()
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (email, password, confirm_pass) values(?,?,?)", (email, senha, confirmar))
        db.commit()
        closedb(db)
        return redirect("/")
    return render_template("cadastrar.html")

@app.route("/chamados")
def chamados():
    db = opendb()
    cursor = db.cursor()
    cursor.execute("SELECT id, cliente, descricao, status, emissao FROM chamados WHERE usuario_id = ?", (USER,))
    chamados = cursor.fetchall()
    return render_template("chamados.html", chamados=chamados)

@app.route("/clientes")
def clientes():
    return render_template("clientes.html")

@app.route("/cadastrar_clientes", methods = ["GET", "POST"])
def cadClientes():
    if request.method == "POST":
        cpf_cnpj = request.form.get("registro")
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        logradouro = request.form.get("logradouro")
        numero = request.form.get("numero")
        bairro = request.form.get("bairro")
        complemento = request.form.get("complemento")
        cidade = request.form.get("cidade")
        uf = request.form.get("uf")
        cep = request.form.get("cep")
        checkElements = [cpf_cnpj, nome, telefone, logradouro, bairro, cidade, uf,]
        for element in checkElements:
            if not element:
                return redirect("/cadastrar_clientes")
        db = opendb()
        cursor = db.cursor()
        cursor.execute("INSERT INTO clientes (nome, usuario_id, cpf_cnpj, telefone, logradouro, bairro, numero, complemento, cidade, uf, cep) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(nome, USER, cpf_cnpj, telefone, logradouro, bairro, numero, complemento, cidade, uf, cep))
        db.commit()
        closedb(db)
        return redirect("/clientes")
    return render_template("cadastrar_clientes.html")

@app.route("/cadastrar_chamados", methods = ["POST", "GET"])
def cadChamados():
    db = opendb()
    cursor = db.cursor()
    entrada = datetime.now()
    entrada = entrada.strftime("%d/%m/%Y %X")
    if request.method == "POST":
        entrada_form = request.form.get("entrada")
        saida_form = request.form.get("saida")
        cliente = request.form.get("cliente")
        situacao = request.form.get("situacao")
        descricao = request.form.get("descricao")
        defeitos = request.form.get("defeitos")
        solucao = request.form.get("solucao")
        checkElements = [entrada_form, cliente, situacao, descricao, defeitos]
        for element in checkElements:
            if not element:
                return redirect("/cadastrar_chamados")
        cursor.execute("INSERT INTO chamados (usuario_id, cliente_id, status, defeitos, emissao, encerramento, descricao, solucao) VALUES (?,?,?,?,?,?,?,?)", (USER, cliente, situacao, defeitos, entrada_form, saida_form, descricao, solucao))
        return redirect("/chamados")
    
    cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id = ?", (USER,))
    clientes = cursor.fetchall()
    closedb(db)
    return render_template("cadastrar_chamados.html", entrada=entrada, clientes=clientes)



if __name__ == "__main__":
    app.run(debug=True)






