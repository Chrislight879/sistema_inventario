import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.docker')

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'postgres'),
                database=os.getenv('DB_NAME', 'sistema_inventario'),
                user=os.getenv('DB_USER', 'admin'),
                password=os.getenv('DB_PASSWORD', 'admin123'),
                port=os.getenv('DB_PORT', '5432')
            )
            print("✅ Conexión exitosa a PostgreSQL en Docker")
            return True
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")
            print(f"   Host: {os.getenv('DB_HOST')}")
            print(f"   DB: {os.getenv('DB_NAME')}")
            print(f"   User: {os.getenv('DB_USER')}")
            return False
    
    def execute_query(self, query, params=None, fetchone=False, fetchall=False):
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                if fetchone:
                    return cursor.fetchone()
                elif fetchall:
                    return cursor.fetchall()
                else:
                    self.conn.commit()
                    return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            print(f"Error en la consulta: {e}")
            return None
    
    def test_connection(self):
        try:
            result = self.execute_query("SELECT version();", fetchone=True)
            if result:
                print(f"📊 PostgreSQL: {result['version']}")
                return True
        except:
            pass
        return False
    
    def init_database(self):
        """Crear tablas si no existen"""
        # El script init-db.sql ya lo hace automáticamente
        print("✅ Base de datos inicializada automáticamente por Docker")
        return True
    
    def close(self):
        if self.conn:
            self.conn.close()

# Instancia global de la base de datos
db = Database()