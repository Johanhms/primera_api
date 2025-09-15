import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuración de la base de datos
# Puedes usar variables de entorno para mayor seguridad en un proyecto real
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Ruta de prueba de la conexión
@app.route('/test-db-connection')
def test_db_connection():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({"message": "¡Conexión a la base de datos exitosa!"})
    else:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

# Ruta principal de la API
@app.route('/')
def home():
    return jsonify({"message": "¡La API está funcionando correctamente!"})



# Nueva ruta para simular la inserción en la tabla de departamentos
@app.route('/departments', methods=['POST'])
def crear_departamento():
    # 1. Obtener los datos del cuerpo de la solicitud
    data = request.json
    
    # 2. Validar que los datos necesarios existan
    if not data or 'department_id' not in data or 'department_name' not in data:
        return jsonify({"error": "Datos incompletos. Se requieren 'department_id' y 'department_name'."}), 400

    department_id = data['department_id']
    department_name = data['department_name']
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

    try:
        cur = conn.cursor()
        
        # 3. Consulta SQL para insertar datos
        # Nota: La tabla no tiene un autoincremento, así que debemos enviar el ID.
        sql_insert = """
        INSERT INTO departments (
            department_id,
            department_name
        ) VALUES (
            %s,
            %s
        );
        """
        
        # 4. Ejecutar la consulta con los datos recibidos
        cur.execute(sql_insert, (department_id, department_name))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": f"Departamento '{department_name}' creado exitosamente."}), 201

    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        return jsonify({"error": "Error al insertar el departamento en la base de datos."}), 500
    
# Nueva ruta para simular la inserción en la tabla de productos
@app.route('/products', methods=['POST'])
def crear_productos():
    # 1. Obtener la lista de productos del cuerpo de la solicitud
    data = request.json
    
    # 2. Validar que los datos sean una lista y que no esté vacía
    if not isinstance(data, list) or not data:
        return jsonify({"error": "Se espera una lista de productos en el cuerpo de la solicitud."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

    inserted_products = []
    try:
        cur = conn.cursor()
        
        # 3. Recorrer la lista y ejecutar la inserción para cada producto
        for product in data:
            # Validar que cada objeto de la lista contenga los campos necesarios
            if 'product_id' not in product or 'product_category_id' not in product or 'product_name' not in product or 'product_price' not in product:
                return jsonify({"error": "Cada producto debe contener 'product_id', 'product_category_id', 'product_name' y 'product_price'."}), 400

            product_id = product['product_id']
            product_category_id = product['product_category_id']
            product_name = product['product_name']
            product_price = product['product_price']
            product_description = product.get('product_description', '')
            product_image = product.get('product_image', '')
            
            # Consulta SQL para insertar un producto
            sql_insert = """
            INSERT INTO products (
                product_id,
                product_category_id,
                product_name,
                product_description,
                product_price,
                product_image
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """
            
            # Ejecutar la consulta con los datos recibidos
            cur.execute(sql_insert, (product_id, product_category_id, product_name, product_description, product_price, product_image))
            inserted_products.append(product_name)

        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": f"Se insertaron {len(inserted_products)} productos exitosamente.", "products_inserted": inserted_products}), 201

    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        return jsonify({"error": "Error al insertar productos en la base de datos."}), 500

    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        return jsonify({"error": "Error al insertar el producto en la base de datos."}), 500    
    
# --- Fin de la nueva ruta ---

if __name__ == '__main__':
    app.run(debug=True)