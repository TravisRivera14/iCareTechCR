from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    # Tabla de productos
    c.execute('''CREATE TABLE IF NOT EXISTS productos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nombre TEXT, categoria TEXT, precio TEXT, imagen TEXT)''')
    # Tabla de textos de la web (Misión, Visión, etc.)
    c.execute('''CREATE TABLE IF NOT EXISTS configuracion
                 (clave TEXT PRIMARY KEY, valor TEXT)''')
    # Valores por defecto si no existen
    c.execute("INSERT OR IGNORE INTO configuracion VALUES ('mision', 'Nuestra misión es...')")
    c.execute("INSERT OR IGNORE INTO configuracion VALUES ('vision', 'Nuestra visión es...')")
    conn.commit()
    conn.close()

@app.route('/api/productos', methods=['POST', 'GET'])
def manejar_productos():
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute("INSERT INTO productos (nombre, categoria, precio, imagen) VALUES (?, ?, ?, ?)",
                  (data['nombre'], data['categoria'], data['precio'], data['imagen']))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "✅ Producto guardado"}), 201
    else:
        c.execute("SELECT * FROM productos")
        prods = [{"id": r[0], "nombre": r[1], "categoria": r[2], "precio": r[3], "imagen": r[4]} for r in c.fetchall()]
        conn.close()
        return jsonify(prods)

@app.route('/api/config', methods=['POST', 'GET'])
def manejar_config():
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        for clave, valor in data.items():
            c.execute("UPDATE configuracion SET valor = ? WHERE clave = ?", (valor, clave))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "✅ Textos actualizados correctamente"})
    else:
        c.execute("SELECT * FROM configuracion")
        config = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        return jsonify(config)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)