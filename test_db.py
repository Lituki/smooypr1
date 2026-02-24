import mysql.connector

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="smooydb",
        port=3306
    )
    if conn.is_connected():
        print("Conexión exitosa a la base de datos")
        # Probar una consulta simple
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tablas en la base de datos:")
        for table in tables:
            print(table[0])
        cursor.close()
    conn.close()
except Exception as e:
    print(f"Error al conectar: {e}")