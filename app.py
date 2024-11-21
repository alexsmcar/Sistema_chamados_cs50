import sqlite3
from datetime import datetime
import math
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta'

USER = 1
SITUACOES = ["aberto", "em andamento", "finalizado"]

def opendb():
    connection = sqlite3.connect("sistema_chamados.db")
    connection.row_factory = sqlite3.Row
    return connection

def closedb(connection):
    connection.close()

@app.route("/")
def index():
    db = opendb()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(status) AS total, COUNT(CASE WHEN status = 'aberto' THEN 1 END) AS aberto, COUNT(CASE WHEN status = 'em andamento' THEN 1 END) AS em_andamento, COUNT(CASE WHEN status = 'finalizado' THEN 1 END) AS finalizado FROM chamados WHERE usuario_id = ?", (USER,))
    dashboard = cursor.fetchone()
    return render_template("dashboard.html", dashboard=dashboard)

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
    pesquisa = request.args.get("pesquisa")
    page = request.args.get("pagina", 1, type=int)
    per_page = 3
    offset = (page - 1) * per_page
    if not pesquisa:
        cursor.execute("SELECT COUNT(*) as total FROM chamados WHERE usuario_id = ?", (USER,))
        total_query = cursor.fetchone()
        total_pages = total_query["total"]
        cursor.execute("SELECT chamados.id, clientes.nome, descricao, status, emissao FROM chamados JOIN clientes ON chamados.cliente_id = clientes.id WHERE chamados.usuario_id = ? LIMIT ? OFFSET ?", (USER, per_page, offset))

    else:
        cursor.execute("SELECT COUNT(*) as total FROM chamados JOIN clientes ON chamados.cliente_id = clientes.id WHERE chamados.usuario_id = ? AND clientes.nome LIKE ?", (USER, "%"+pesquisa+"%"))
        total_query = cursor.fetchone()
        total_pages = total_query["total"]
        cursor.execute("SELECT chamados.id, clientes.nome, descricao, status, emissao FROM chamados JOIN clientes ON chamados.cliente_id = clientes.id WHERE chamados.usuario_id = ? AND clientes.nome LIKE ? LIMIT ? OFFSET ?", (USER, "%"+pesquisa+"%", per_page, offset))

    chamados = cursor.fetchall()
    total_pages = math.ceil((total_pages / per_page))
    closedb(db)
    return render_template("chamados.html", chamados=chamados, page=page, total_pages=total_pages)

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
    if request.method == "POST":
        entrada = request.form.get("entrada")
        saida = request.form.get("saida")
        cliente = request.form.get("cliente")
        situacao = request.form.get("situacao")
        descricao = request.form.get("descricao")
        defeitos = request.form.get("defeitos")
        solucao = request.form.get("solucao")
        checkElements = [entrada, cliente, situacao, descricao, defeitos]
        for element in checkElements:
            if not element:
                return redirect("/cadastrar_chamados")
        cursor.execute("INSERT INTO chamados (usuario_id, cliente_id, status, defeitos, emissao, encerramento, descricao, solucao) VALUES (?,?,?,?,?,?,?,?)", (USER, cliente, situacao, defeitos, entrada, saida, descricao, solucao))
        db.commit()
        return redirect("/chamados")
    
    cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id = ?", (USER,))
    clientes = cursor.fetchall()
    closedb(db)
    return render_template("cadastrar_chamados.html", clientes=clientes, situacoes=SITUACOES)

@app.route("/editar_chamado")
def editar_chamado():
    db = opendb()
    cursor = db.cursor()
    chamado_id = request.args.get("chamado")
    cursor.execute("SELECT chamados.*, clientes.nome AS nome_cliente, clientes.id AS id_cliente FROM chamados JOIN clientes ON chamados.cliente_id = clientes.id WHERE chamados.id = ? AND chamados.usuario_id = ?", (chamado_id, USER))
    chamado = cursor.fetchone()
    cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id = ?", (USER,))
    clientes = cursor.fetchall()
    closedb(db)
    return render_template("cadastrar_chamados.html", chamado=chamado, situacoes=SITUACOES, clientes=clientes)


if __name__ == "__main__":
    app.run(debug=True)






