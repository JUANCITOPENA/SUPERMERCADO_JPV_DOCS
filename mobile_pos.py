from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from src.config.database import db
from src.controllers.sales_controller import SalesController
from src.controllers.auth_controller import AuthController
from src.utils.print_engine import PrintEngine
import socket
import json
import os
import traceback

app = Flask(__name__)
CORS(app)

# Carpeta maestra de almacenamiento local
BASE_STORAGE = os.path.join(os.getcwd(), "ventas_generadas")
if not os.path.exists(BASE_STORAGE):
    os.makedirs(BASE_STORAGE)

auth_ctrl = AuthController()
sales_ctrl = SalesController()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return "127.0.0.1"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(BASE_STORAGE, filename, as_attachment=True)

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        res = auth_ctrl.login(data.get('username'), data.get('password'))
        if res:
            conn = db.connect()
            v_row = conn.cursor().execute("SELECT TOP 1 ID_VENDEDOR, VENDEDOR FROM VENDEDOR WHERE VENDEDOR LIKE ?", (f"%{data.get('username')}%",)).fetchone()
            if not v_row: v_row = conn.cursor().execute("SELECT TOP 1 ID_VENDEDOR, VENDEDOR FROM VENDEDOR").fetchone()
            conn.close()
            return jsonify({"success": True, "user": {"id": res[0], "role": res[1]}, "vendor": {"id": v_row[0], "name": v_row[1]}})
        return jsonify({"success": False, "msg": "Credenciales invalidas"}), 401
    except Exception as e: return jsonify({"success": False, "msg": str(e)}), 500

@app.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        clients = sales_ctrl.get_clients()
        return jsonify([{"id": c[0], "name": c[1], "rnc": c[2], "type": c[3]} for c in clients])
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = db.connect()
        rows = conn.cursor().execute("SELECT P.ID_PRODUCTO, P.PRODUCTO, P.PRECIO_VENTA, P.STOCK, ISNULL(FP.foto_Productos_url, '') FROM PRODUCTO P LEFT JOIN FOTO_PRODUCTOS FP ON P.ID_PRODUCTO = FP.ID_PRODUCTO WHERE P.STOCK > 0").fetchall()
        conn.close()
        return jsonify([{"id": p[0], "name": p[1], "price": float(p[2]), "stock": p[3], "image": p[4]} for p in rows])
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/checkout', methods=['POST'])
def checkout():
    try:
        data = request.json
        items = data.get('items')
        
        # 1. Calcular totales preliminares
        subtotal = 0
        itbis = 0
        for it in items:
            subtotal += it['qty'] * it['price']
            itbis += it['qty'] * it.get('itbis_unit', 0)
        total = subtotal + itbis
        
        # 2. Procesar venta en DB
        ok, res = sales_ctrl.process_full_sale(data.get('client_id'), data.get('vendor_id'), items, 1, 1, total, subtotal, itbis)
        
        if ok:
            # 3. Preparar datos para PDFs
            conn = db.connect()
            c_row = conn.cursor().execute("SELECT NOMBRE_CLIENTE + ' ' + APELLIDO_CLIENTE, RNC_CEDULA FROM CLIENTE WHERE ID_CLIENTE=?", (data.get('client_id'),)).fetchone()
            conn.close()
            
            res['client_name'] = c_row[0] if c_row else "Consumidor Final"
            res['client_rnc'] = c_row[1] if c_row else "N/A"
            res['subtotal'] = subtotal
            res['itbis'] = itbis
            res['total'] = total

            # Formatear items para el generador
            pdf_items = []
            for it in items:
                pdf_items.append({
                    "id": it['id'],
                    "name": it['name'],
                    "qty": it['qty'],
                    "price": it['price'],
                    "total": it['qty'] * it['price']
                })

            # 4. Generar archivos localmente (sin abrirlos en el servidor)
            tk_name = f"ticket_{res['ncf']}.pdf"
            tk_path = os.path.join(BASE_STORAGE, tk_name)
            PrintEngine.generate_thermal_ticket_pdf(res, pdf_items, filename=tk_path)
            
            inv_name = f"factura_{res['ncf']}.pdf"
            inv_path = os.path.join(BASE_STORAGE, inv_name)
            PrintEngine.generate_invoice(res, pdf_items, filename=inv_path)

            return jsonify({
                "success": True, 
                "ticket_url": f"/download/{tk_name}",
                "invoice_url": f"/download/{inv_name}",
                "ncf": res['ncf'],
                "id": res['id']
            })
        else:
            return jsonify({"success": False, "msg": str(res)}), 500
            
    except Exception as e:
        print("--- ERROR EN CHECKOUT ---")
        traceback.print_exc()
        return jsonify({"success": False, "msg": f"Error interno: {str(e)}"}), 500

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"🚀 Mobile POS Server running on http://{local_ip}:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
