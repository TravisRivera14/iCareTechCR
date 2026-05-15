from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

# static_folder='.' le dice a Flask que tus archivos están en la carpeta principal
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    c.execute(query, params)
    res = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return res

def init_db():
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, precio TEXT, imagen TEXT, categoria TEXT DEFAULT 'Otros')''')
    c.execute('''CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY, valor TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS servicios (id INTEGER PRIMARY KEY AUTOINCREMENT, icono TEXT, titulo TEXT, descripcion TEXT, imagen TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS socios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, imagen TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS resenas (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, puesto TEXT, comentario TEXT, imagen_cliente TEXT, estrellas INTEGER DEFAULT 5)''')
    conn.commit()
    conn.close()

init_db()

# --- ESTAS LÍNEAS ARREGLAN EL "NOT FOUND" ---
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/admin')
def admin():
    return app.send_static_file('admin.html')
# --------------------------------------------

@app.route('/api/todo', methods=['GET'])
def obtener_todo():
    servicios = db_query("SELECT * FROM servicios", fetch=True)
    productos = db_query("SELECT * FROM productos", fetch=True)
    socios = db_query("SELECT * FROM socios", fetch=True)
    resenas = db_query("SELECT * FROM resenas", fetch=True)
    config_raw = db_query("SELECT * FROM configuracion", fetch=True)
    config = {row[0]: row[1] for row in config_raw}
    return jsonify({
        "servicios": [{"id": s[0], "icono": s[1], "titulo": s[2], "descripcion": s[3], "imagen": s[4]} for s in servicios],
        "productos": [{"id": p[0], "nombre": p[1], "precio": p[2], "imagen": p[3], "categoria": p[4]} for p in productos],
        "socios": [{"id": so[0], "nombre": so[1], "imagen": so[2]} for so in socios],
        "resenas": [{"id": r[0], "cliente": r[1], "puesto": r[2], "comentario": r[3], "imagen_cliente": r[4]} for r in resenas],
        "config": config
    })

# ... (Mantén el resto de tus rutas de la API igual)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)