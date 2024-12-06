import sqlite3
from datetime import datetime
import math
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



SITUACOES = ["aberto", "em andamento", "finalizado"]

def opendb():
    connection = sqlite3.connect("sistema_chamados.db")
    connection.row_factory = sqlite3.Row
    return connection

def closedb(connection, cursor):
    cursor.close()
    connection.close()

@app.context_processor
def inject_user_email():
    db = opendb()
    cursor = db.cursor()
    user_id = session.get("user_id")
    if user_id:
        cursor.execute("SELECT email FROM usuarios WHERE id = ?", (user_id,))
        user_email = cursor.fetchone()
        return {
            "user_email" : user_email["email"]
        }
    return {}

@app.route("/")
@login_required
def index():
    db = opendb()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(status) AS total, COUNT(CASE WHEN status = 'aberto' THEN 1 END) AS aberto, COUNT(CASE WHEN status = 'em andamento' THEN 1 END) AS em_andamento, COUNT(CASE WHEN status = 'finalizado' THEN 1 END) AS finalizado FROM chamados WHERE usuario_id = ?", (session["user_id"],))
    dashboard = cursor.fetchone()
    closedb(db, cursor)
    return render_template("dashboard.html", dashboard=dashboard)

@app.route("/login", methods = ["GET", "POST"])
def login():
        db = opendb()
        cursor = db.cursor()
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")
            if not email or not senha:
                return redirect("/login") # campo não preenchidos
            cursor.execute("SELECT id, password FROM usuarios WHERE email = ?",(email,))
            usuario = cursor.fetchone()
            if not usuario or not check_password_hash(usuario["password"], senha):
                return redirect("/login") #usuario ou senha incorreta
            else:
                session["user_id"] = usuario["id"]
                return redirect("/")
        closedb(db, cursor)
        return render_template("login.html")


@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    db = opendb()
    cursor = db.cursor()
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar")
        if not email or not senha or not confirmar:
            return redirect("/cadastrar")
        cursor.execute("SELECT email FROM usuarios WHERE email = ?",(email,))
        email_db = cursor.fetchall()
        if not email_db and senha == confirmar:
            senha = generate_password_hash(senha)
            cursor.execute("INSERT INTO usuarios (email, password) values(?,?)", (email, senha))
            db.commit()
            return redirect("/login") # retorna pagina de login
    closedb(db, cursor)
    return render_template("cadastrar.html")


@app.route("/chamados")
@login_required
def chamados():
    db = opendb()
    cursor = db.cursor()
    pesquisa = request.args.get("pesquisa")
    page = request.args.get("pagina", 1, type=int)
    per_page = 8
    offset = (page - 1) * per_page
    if not pesquisa:
        cursor.execute("SELECT COUNT(*) as total FROM chamados WHERE usuario_id = ?", (session["user_id"],))
        total_query = cursor.fetchone()
        total_pages = total_query["total"]
        cursor.execute("SELECT chamados.id, clientes.nome, descricao, status, emissao FROM chamados JOIN clientes ON chamados.cliente_id = clientes.id WHERE chamados.usuario_id = ? LIMIT ? OFFSET ?", (session["user_id"], per_page, offset))

    else:
        cursor.execute("SELECT COUNT(*) as total FROM chamados JOIN clientes ON chamados.cliente_id = clientes.id WHERE chamados.usuario_id = ? AND (clientes.nome LIKE ? or clientes.id = ?)", (session["user_id"], "%"+pesquisa+"%", pesquisa))
        total_query = cursor.fetchone()
        total_pages = total_query["total"]
        cursor.execute("SELECT chamados.id, clientes.nome, descricao, status, emissao FROM chamados JOIN clientes ON chamados.cliente_id = clientes.id WHERE chamados.usuario_id = ? AND (clientes.nome LIKE ? OR clientes.id = ?) LIMIT ? OFFSET ?", (session["user_id"], "%"+pesquisa+"%",pesquisa, per_page, offset))

    chamados = cursor.fetchall()
    total_pages = math.ceil((total_pages / per_page))
    if total_pages < 1:
        total_pages = 1
    closedb(db, cursor)
    return render_template("chamados.html", chamados=chamados, page=page, total_pages=total_pages, pesquisa=pesquisa)


@app.route("/clientes")
@login_required
def clientes():
    db = opendb()
    cursor = db.cursor()
    pesquisa = request.args.get("pesquisa")
    page = request.args.get("pagina", 1, type=int)
    per_page = 8
    offset = (page - 1) * per_page
    if not pesquisa:
        cursor.execute("SELECT COUNT(*) AS total FROM clientes WHERE usuario_id = ?", (session["user_id"],))
        total_query = cursor.fetchone()
        total_pages = total_query['total']
        cursor.execute("SELECT id, nome, cpf_cnpj FROM clientes WHERE usuario_id = ? LIMIT ? OFFSET ?",(session["user_id"], per_page, offset))
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM clientes WHERE usuario_id = ? AND (nome LIKE ? or id = ?)",(session["user_id"], "%"+pesquisa+"%", pesquisa))
        total_query = cursor.fetchone()
        total_pages = total_query["total"]
        cursor.execute("SELECT id, nome, cpf_cnpj FROM clientes WHERE usuario_id = ? AND (nome LIKE ? or id = ?) LIMIT ? OFFSET ?",(session["user_id"], "%"+pesquisa+"%", pesquisa, per_page, offset))
    clientes = cursor.fetchall()
    total_pages = math.ceil((total_pages / per_page))
    if total_pages < 1:
        total_pages = 1
    closedb(db, cursor)
    return render_template("clientes.html", clientes=clientes, page=page, total_pages=total_pages, pesquisa=pesquisa)



@app.route("/cadastrar_clientes", methods = ["GET", "POST"])
@login_required
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
        cursor.execute("INSERT INTO clientes (nome, usuario_id, cpf_cnpj, telefone, logradouro, bairro, numero, complemento, cidade, uf, cep) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(nome, session["user_id"], cpf_cnpj, telefone, logradouro, bairro, numero, complemento, cidade, uf, cep))
        db.commit()
        closedb(db, cursor)
        return redirect("/clientes")
    action = 'criar_cliente'
    return render_template("cadastrar_clientes.html", action=action)

@app.route("/cadastrar_chamados", methods = ["POST", "GET"])
@login_required
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
        entrada = datetime.strptime(entrada, "%Y-%m-%dT%H:%M")
        entrada = entrada.strftime("%d/%m/%Y %H:%M")
        if saida:
            saida = datetime.strptime(saida, "%Y-%m-%dT%H:%M")
            saida = saida.strftime("%d/%m/%Y %H:%M")
        cursor.execute("INSERT INTO chamados (usuario_id, cliente_id, status, defeitos, emissao, encerramento, descricao, solucao) VALUES (?,?,?,?,?,?,?,?)", (session["user_id"], cliente, situacao, defeitos, entrada, saida, descricao, solucao))
        db.commit()
        return redirect("/chamados")
    action = "criar_chamado"
    cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id = ? ORDER BY nome", (session["user_id"],))
    clientes = cursor.fetchall()
    closedb(db, cursor)
    return render_template("cadastrar_chamados.html", clientes=clientes, situacoes=SITUACOES, action=action)

@app.route("/editar_chamado", methods=["GET", "POST"])
@login_required
def editar_chamado():
    db = opendb()
    cursor = db.cursor()
    if request.method == "POST":
        id_chamado = request.form.get("cod")
        entrada = request.form.get("entrada")
        saida = request.form.get("saida")
        cliente = request.form.get("cliente")
        situacao = request.form.get("situacao")
        descricao = request.form.get("descricao")
        defeitos = request.form.get("defeitos")
        solucao = request.form.get("solucao")
        entrada = datetime.strptime(entrada, "%Y-%m-%dT%H:%M")
        entrada = entrada.strftime("%d/%m/%Y %H:%M")
        checkElements = [entrada, cliente, situacao, descricao, defeitos]
        for element in checkElements:
            if not element:
                return redirect("/editar_chamado")
        if saida:
            saida = datetime.strptime(saida, "%Y-%m-%dT%H:%M")
            saida = saida.strftime("%d/%m/%Y %H:%M")
        cursor.execute("UPDATE chamados SET cliente_id = ?, status = ?, defeitos = ?, emissao = ?, encerramento = ?, descricao = ?, solucao = ? WHERE id = ? and usuario_id = ?", (cliente, situacao, defeitos, entrada, saida, descricao, solucao, id_chamado, session["user_id"]))
        db.commit()
        return redirect("/chamados")
    chamado_id = request.args.get("chamado")
    cursor.execute("SELECT chamados.*, clientes.nome AS nome_cliente, clientes.id AS id_cliente FROM chamados JOIN clientes ON chamados.cliente_id = clientes.id WHERE chamados.id = ? AND chamados.usuario_id = ?", (chamado_id, session["user_id"]))
    chamado = cursor.fetchone()
    entrada = chamado["emissao"]
    entrada = datetime.strptime(entrada, "%d/%m/%Y %H:%M")
    entrada = entrada.strftime("%Y-%m-%dT%H:%M")
    saida = chamado["encerramento"]
    if saida:
        saida = datetime.strptime(chamado["encerramento"], "%d/%m/%Y %H:%M")
        saida = saida.strftime("%Y-%m-%dT%H:%M")
    action = "atualizar_chamado"
    cursor.execute("SELECT id, nome FROM clientes WHERE usuario_id = ? ORDER BY nome", (session["user_id"],))
    clientes = cursor.fetchall()
    closedb(db, cursor)
    return render_template("cadastrar_chamados.html", chamado=chamado, situacoes=SITUACOES, clientes=clientes, entrada=entrada, saida=saida, action=action)

@app.route("/editar_cliente", methods=["GET", "POST"])
@login_required
def editar_cliente():
    db = opendb()
    cursor = db.cursor()
    if request.method == "POST":
        id_cliente = request.form.get("cod")
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
                return redirect("/editar_cliente")
        cursor.execute("UPDATE clientes SET nome = ?, cpf_cnpj = ?, telefone = ?, logradouro = ?, bairro = ?, numero = ?, complemento = ?, cidade = ?, uf = ?, cep = ? WHERE id = ? AND usuario_id = ? ", (nome, cpf_cnpj, telefone, logradouro, bairro, numero, complemento, cidade, uf, cep, id_cliente, session["user_id"]))
        db.commit()
        return redirect("/clientes")
    cliente_id = request.args.get("cliente")
    action = "atualizar_cliente"
    cursor.execute("SELECT * FROM clientes WHERE id = ? AND usuario_id = ? ", (cliente_id,session["user_id"]))
    cliente = cursor.fetchone()
    closedb(db, cursor)
    return render_template("cadastrar_clientes.html",cliente=cliente, action=action)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)






