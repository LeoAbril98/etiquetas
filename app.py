from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
from generate_pdf import generate_etiquetas_pdf
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necessário para exibir mensagens flash

# Criar banco de dados se não existir
def init_db():
    conn = sqlite3.connect("etiquetas.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY, 
        nome TEXT, 
        cep TEXT,
        rua TEXT,
        numero TEXT,  
        bairro TEXT,
        cidade TEXT,
        estado TEXT,
        telefone TEXT 
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transportadoras (
        id INTEGER PRIMARY KEY,
        nome TEXT UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cliente_transportadora (
        cliente_id INTEGER,
        transportadora_id INTEGER,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(transportadora_id) REFERENCES transportadoras(id),
        PRIMARY KEY (cliente_id, transportadora_id)
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect("etiquetas.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()
    c.execute("SELECT * FROM transportadoras")
    transportadoras = c.fetchall()
    conn.close()
    return render_template("index.html", clientes=clientes, transportadoras=transportadoras)

@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    nome = request.form["nome"]
    cep = request.form["cep"]
    rua = request.form["rua"]
    numero = request.form["numero"]  
    bairro = request.form["bairro"]
    cidade = request.form["cidade"]
    estado = request.form["estado"]
    telefone = request.form["telefone"]
    
    conn = sqlite3.connect("etiquetas.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO clientes (nome, cep, rua, numero, bairro, cidade, estado, telefone) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, cep, rua, numero, bairro, cidade, estado, telefone))
    conn.commit()
    conn.close()
    
    flash("Cliente cadastrado com sucesso!")
    return redirect(url_for("index"))

@app.route("/editar_cliente", methods=["POST"])
def editar_cliente():
    cliente_id = request.form["cliente_id"]
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")

    conn = sqlite3.connect("etiquetas.db")
    c = conn.cursor()
    
    if nome:
        c.execute("UPDATE clientes SET nome = ? WHERE id = ?", (nome, cliente_id))
    if telefone:
        c.execute("UPDATE clientes SET telefone = ? WHERE id = ?", (telefone, cliente_id))
    
    conn.commit()
    conn.close()
    
    flash("Cliente atualizado com sucesso!")
    return redirect(url_for("index"))

@app.route("/deletar_cliente", methods=["POST"])
def deletar_cliente():
    cliente_id = request.form["cliente_id"]
    
    conn = sqlite3.connect("etiquetas.db")
    c = conn.cursor()
    c.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    conn.close()
    
    flash("Cliente excluído com sucesso!")
    return redirect(url_for("index"))

@app.route("/add_transportadora", methods=["POST"])
def add_transportadora():
    nome_transportadora = request.form["nome_transportadora"]
    
    conn = sqlite3.connect("etiquetas.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO transportadoras (nome) VALUES (?)", (nome_transportadora,))
        conn.commit()
        flash("Transportadora cadastrada com sucesso!")
    except sqlite3.IntegrityError:
        flash("Transportadora já existe!")
    finally:
        conn.close()
    
    return redirect(url_for("index"))

@app.route("/buscar_cep", methods=["GET"])
def buscar_cep():
    cep = request.args.get("cep")
    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    return response.json()

@app.route("/gerar_etiquetas", methods=["POST"])
def gerar_etiquetas():
    cliente_id = request.form["cliente_id"]
    transportadora_id = request.form["transportadora_id"]
    num_etiquetas = int(request.form["num_etiquetas"])
    
    conn = sqlite3.connect("etiquetas.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,))
    cliente = c.fetchone()
    c.execute("SELECT nome FROM transportadoras WHERE id=?", (transportadora_id,))
    transportadora = c.fetchone()
    
    if transportadora:
        transportadora_nome = transportadora[0]
        c.execute("INSERT OR IGNORE INTO cliente_transportadora (cliente_id, transportadora_id) VALUES (?, ?)", (cliente_id, transportadora_id))
        conn.commit()
    else:
        transportadora_nome = "Nenhuma transportadora"
    
    conn.close()
    
    if cliente:
        pdf_path = generate_etiquetas_pdf(cliente + (transportadora_nome,), num_etiquetas)
        return send_file(pdf_path, as_attachment=True)

    return "Erro ao gerar etiquetas", 400

if __name__ == "__main__":
    app.run(debug=True)
