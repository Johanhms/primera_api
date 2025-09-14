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
    
# --- Fin de la nueva ruta ---

if __name__ == '__main__':
    app.run(debug=True)