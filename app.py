from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

# Configuración para servir archivos desde la raíz
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

# --- RUTAS DE NAVEGACIÓN ---
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/admin')
def admin():
    return app.send_static_file('admin.html')

# --- API ---
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

@app.route('/api/config', methods=['POST'])
def guardar_config():
    d = request.json
    for k, v in d.items():
        db_query("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (k, v))
    return jsonify({"mensaje": "✅"})

@app.route('/api/servicios', methods=['POST'])
@app.route('/api/servicios/<int:id>', methods=['PUT'])
def gestionar_servicio(id=None):
    d = request.json
    if request.method == 'POST':
        db_query("INSERT INTO servicios (icono, titulo, descripcion, imagen) VALUES (?, ?, ?, ?)", (d['icono'], d['titulo'], d['descripcion'], d.get('imagen','')))
    else:
        db_query("UPDATE servicios SET icono=?, titulo=?, descripcion=?, imagen=? WHERE id=?", (d['icono'], d['titulo'], d['descripcion'], d.get('imagen',''), id))
    return jsonify({"mensaje": "✅"})

@app.route('/api/productos', methods=['POST'])
@app.route('/api/productos/<int:id>', methods=['PUT'])
def gestionar_producto(id=None):
    d = request.json
    if request.method == 'POST':
        db_query("INSERT INTO productos (nombre, precio, imagen, categoria) VALUES (?, ?, ?, ?)", (d['nombre'], d['precio'], d['imagen'], d.get('categoria', 'Otros')))
    else:
        db_query("UPDATE productos SET nombre=?, precio=?, imagen=?, categoria=? WHERE id=?", (d['nombre'], d['precio'], d['imagen'], d.get('categoria', 'Otros'), id))
    return jsonify({"mensaje": "✅"})

@app.route('/api/resenas', methods=['POST'])
@app.route('/api/resenas/<int:id>', methods=['PUT'])
def gestionar_resena(id=None):
    d = request.json
    if request.method == 'POST':
        db_query("INSERT INTO resenas (cliente, puesto, comentario, imagen_cliente) VALUES (?, ?, ?, ?)", (d['cliente'], d.get('puesto',''), d['comentario'], d.get('imagen_cliente','')))
    else:
        db_query("UPDATE resenas SET cliente=?, puesto=?, comentario=?, imagen_cliente=? WHERE id=?", (d['cliente'], d.get('puesto',''), d['comentario'], d.get('imagen_cliente',''), id))
    return jsonify({"mensaje": "✅"})

@app.route('/api/socios', methods=['POST'])
def guardar_socio():
    d = request.json
    db_query("INSERT INTO socios (nombre, imagen) VALUES (?, ?)", (d['nombre'], d['imagen']))
    return jsonify({"mensaje": "✅"})

@app.route('/api/eliminar/<tabla>/<int:id>', methods=['DELETE'])
def eliminar_item(tabla, id):
    if tabla in ['servicios', 'productos', 'socios', 'resenas']:
        db_query(f"DELETE FROM {tabla} WHERE id = ?", (id,))
    return jsonify({"mensaje": "🗑️"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))