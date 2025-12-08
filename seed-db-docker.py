#!/usr/bin/env python3
import psycopg2
import os
import sys
from datetime import date

def conectar_db():
    """Conectar a la base de datos desde Docker"""
    try:
        print("🔗 Conectando a PostgreSQL...")
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'postgres'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'sistema_inventario'),
            user=os.getenv('DB_USER', 'admin'),
            password=os.getenv('DB_PASSWORD', 'admin123')
        )
        print("✅ Conexión exitosa a PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)

def reiniciar_base_datos(cursor):
    """Reiniciar completamente la base de datos (más agresivo)"""
    print("🔄 Reiniciando base de datos...")
    
    # Desactivar constraints temporalmente
    cursor.execute("SET session_replication_role = 'replica';")
    
    # Tablas en orden de dependencia (de más dependiente a menos)
    tablas = [
        'Relacion_Entre_Compras',
        'Mantenimientos',
        'AsignadorCompra',
        'Usuarios',
        'Productos',
        'Proveedores',
        'Ubicaciones',
        'Categorias'
    ]
    
    # Usar TRUNCATE con CASCADE para limpiar todo y reiniciar secuencias
    for tabla in tablas:
        try:
            cursor.execute(f"TRUNCATE TABLE {tabla} CASCADE;")
            print(f"  ✅ {tabla} truncada y secuencia reiniciada")
        except Exception as e:
            print(f"⚠️  Error con {tabla}: {e}")
    
    # Reactivar constraints
    cursor.execute("SET session_replication_role = 'origin';")
    print("✅ Base de datos reiniciada completamente")

def insertar_categorias(cursor):
    """Insertar categorías de ejemplo"""
    categorias = [
        'Electrónicos', 'Muebles', 'Equipo de Oficina', 'Software',
        'Herramientas', 'Consumibles', 'Redes y Telecomunicaciones',
        'Seguridad', 'Iluminación', 'Climatización'
    ]
    
    for categoria in categorias:
        cursor.execute("INSERT INTO Categorias (Nombre_Categoria) VALUES (%s)", (categoria,))
    print(f"✅ {len(categorias)} categorías insertadas")

def insertar_proveedores(cursor):
    """Insertar proveedores de ejemplo"""
    proveedores = [
        'Tecnología Avanzada SA', 'Muebles Corporativos SL', 'Distribuidora Oficina',
        'Software Solutions', 'Herramientas Profesionales', 'Electrónica Global',
        'Suministros Industriales', 'Redes y Conectividad', 'Seguridad Integral',
        'Climatización y Ventilación'
    ]
    
    for proveedor in proveedores:
        cursor.execute("INSERT INTO Proveedores (Nombre) VALUES (%s)", (proveedor,))
    print(f"✅ {len(proveedores)} proveedores insertados")

def insertar_ubicaciones(cursor):
    """Insertar ubicaciones de ejemplo"""
    ubicaciones = [
        ('Edificio Central - Piso 1', 'Piso 1'),
        ('Edificio Central - Piso 2', 'Piso 2'),
        ('Edificio Central - Piso 3', 'Piso 3'),
        ('Sucursal Norte', 'Norte'),
        ('Sucursal Sur', 'Sur'),
        ('Almacén Principal', 'Almacén'),
        ('Oficina Administrativa', 'Admin'),
        ('Laboratorio de Investigación', 'Laboratorio'),
        ('Sala de Servidores', 'Servidores'),
        ('Área de Recepción', 'Recepción'),
        ('Sala de Juntas', 'Juntas'),
        ('Taller de Mantenimiento', 'Taller')
    ]
    
    for nombre, descripcion in ubicaciones:
        cursor.execute("INSERT INTO Ubicaciones (NombreEdificio) VALUES (%s)", (nombre,))
    print(f"✅ {len(ubicaciones)} ubicaciones insertadas")

def insertar_usuarios(cursor):
    """Insertar usuarios de ejemplo usando nombres de ubicaciones"""
    # Obtener ubicaciones por nombre
    cursor.execute("SELECT IdUbicacion, NombreEdificio FROM Ubicaciones")
    ubicaciones_map = {nombre: id for id, nombre in cursor.fetchall()}
    
    usuarios = [
        # (nombre, nombre_ubicacion, ubicacion_especifica)
        ('Juan Pérez', 'Edificio Central - Piso 1', 'Oficina 101'),
        ('María González', 'Edificio Central - Piso 1', 'Oficina 102'),
        ('Carlos López', 'Edificio Central - Piso 2', 'Cubículo A'),
        ('Ana Martínez', 'Edificio Central - Piso 2', 'Cubículo B'),
        ('Pedro Rodríguez', 'Edificio Central - Piso 3', 'Sala de Proyectos'),
        ('Laura Sánchez', 'Sucursal Norte', 'Gerencia'),
        ('Miguel Torres', 'Sucursal Sur', 'Almacén'),
        ('Sofía Ramírez', 'Almacén Principal', 'Recepción'),
        ('David Flores', 'Laboratorio de Investigación', 'Laboratorio'),
        ('Elena Cruz', 'Sala de Servidores', 'Sala de Servidores')
    ]
    
    usuarios_insertados = 0
    for nombre, nombre_ubicacion, ubicacion_especifica in usuarios:
        ubicacion_id = ubicaciones_map.get(nombre_ubicacion)
        if ubicacion_id:
            cursor.execute(
                "INSERT INTO Usuarios (Nombre, Ubicacion, Ubicacion_Especifica) VALUES (%s, %s, %s)",
                (nombre, ubicacion_id, ubicacion_especifica)
            )
            usuarios_insertados += 1
        else:
            print(f"⚠️  Ubicación '{nombre_ubicacion}' no encontrada para usuario {nombre}")
    
    print(f"✅ {usuarios_insertados} usuarios insertados")

def insertar_productos(cursor):
    """Insertar productos de ejemplo"""
    # Obtener categorías por nombre
    cursor.execute("SELECT IdCategoria, Nombre_Categoria FROM Categorias")
    categorias_map = {nombre: id for id, nombre in cursor.fetchall()}
    
    productos = [
        # Productos MADRE
        ('Laptop Dell XPS 15', 'Electrónicos', True),
        ('Computadora de Escritorio HP', 'Electrónicos', True),
        ('Servidor Rack Dell', 'Electrónicos', True),
        ('Silla Ergonómica Ejecutiva', 'Muebles', True),
        ('Escritorio de Oficina', 'Muebles', True),
        ('Impresora Multifuncional', 'Equipo de Oficina', True),
        ('Microsoft Office 365', 'Software', True),
        ('Taladro Inalámbrico', 'Herramientas', True),
        ('Router Cisco', 'Redes y Telecomunicaciones', True),
        ('Aire Acondicionado', 'Climatización', True),
        
        # Productos HIJO
        ('Memoria RAM 16GB DDR4', 'Electrónicos', False),
        ('SSD 1TB NVMe', 'Electrónicos', False),
        ('Disco Duro 2TB', 'Electrónicos', False),
        ('Tarjeta Gráfica NVIDIA RTX 4060', 'Electrónicos', False),
        ('Fuente de Poder 750W', 'Electrónicos', False),
        ('Monitor LG 27" 4K', 'Electrónicos', False),
        ('Teclado Mecánico', 'Equipo de Oficina', False),
        ('Mouse Inalámbrico', 'Equipo de Oficina', False),
        ('Tóner para Impresora', 'Consumibles', False),
        ('Cámara de Seguridad', 'Seguridad', False),
        ('Lámpara LED', 'Iluminación', False)
    ]
    
    productos_insertados = 0
    for nombre, nombre_categoria, es_madre in productos:
        categoria_id = categorias_map.get(nombre_categoria)
        if categoria_id:
            cursor.execute(
                "INSERT INTO Productos (Nombre, Categoria, Es_Producto_Madre) VALUES (%s, %s, %s)",
                (nombre, categoria_id, es_madre)
            )
            productos_insertados += 1
        else:
            print(f"⚠️  Categoría '{nombre_categoria}' no encontrada")
    
    print(f"✅ {productos_insertados} productos insertados")

def insertar_compras(cursor):
    """Insertar compras de ejemplo"""
    # Obtener mapeos
    cursor.execute("SELECT IdProducto, Nombre FROM Productos")
    productos_map = {nombre: id for id, nombre in cursor.fetchall()}
    
    cursor.execute("SELECT IdProveedor, Nombre FROM Proveedores")
    proveedores_map = {nombre: id for id, nombre in cursor.fetchall()}
    
    cursor.execute("SELECT IdUsuario, Nombre FROM Usuarios")
    usuarios_map = {nombre: id for id, nombre in cursor.fetchall()}
    
    compras = [
        # (fecha, nombre_producto, nombre_proveedor, fin_garantia, nombre_usuario, numero_serie)
        (date(2024, 1, 15), 'Laptop Dell XPS 15', 'Tecnología Avanzada SA', date(2025, 1, 15), 'Juan Pérez', 'SN001'),
        (date(2024, 2, 20), 'Computadora de Escritorio HP', 'Muebles Corporativos SL', date(2025, 2, 20), 'María González', 'SN002'),
        (date(2024, 3, 10), 'Servidor Rack Dell', 'Distribuidora Oficina', date(2025, 3, 10), 'Carlos López', 'SN003'),
        (date(2024, 4, 5), 'Silla Ergonómica Ejecutiva', 'Software Solutions', date(2025, 4, 5), 'Ana Martínez', 'SN004'),
        (date(2024, 5, 12), 'Escritorio de Oficina', 'Herramientas Profesionales', date(2025, 5, 12), 'Pedro Rodríguez', 'SN005'),
        (date(2024, 6, 18), 'Microsoft Office 365', 'Electrónica Global', date(2025, 6, 18), 'Laura Sánchez', 'LIC001'),
        (date(2024, 7, 22), 'Impresora Multifuncional', 'Suministros Industriales', date(2025, 7, 22), 'Miguel Torres', 'SN007'),
        (date(2024, 8, 30), 'Taladro Inalámbrico', 'Redes y Conectividad', date(2025, 8, 30), 'Sofía Ramírez', 'SN008'),
        (date(2024, 9, 14), 'Router Cisco', 'Seguridad Integral', date(2026, 9, 14), 'David Flores', 'SN009'),
        (date(2024, 10, 8), 'Aire Acondicionado', 'Climatización y Ventilación', date(2026, 10, 8), 'Elena Cruz', 'SN010'),
        # Compras adicionales para productos hijo
        (date(2024, 1, 20), 'Memoria RAM 16GB DDR4', 'Tecnología Avanzada SA', date(2025, 1, 20), 'Juan Pérez', 'SN011'),
        (date(2024, 1, 25), 'SSD 1TB NVMe', 'Tecnología Avanzada SA', date(2025, 1, 25), 'Juan Pérez', 'SN012'),
        (date(2024, 2, 10), 'Monitor LG 27" 4K', 'Muebles Corporativos SL', date(2025, 2, 10), 'María González', 'SN013')
    ]
    
    compras_insertadas = 0
    for fecha, nombre_producto, nombre_proveedor, fin_garantia, nombre_usuario, numero_serie in compras:
        producto_id = productos_map.get(nombre_producto)
        proveedor_id = proveedores_map.get(nombre_proveedor)
        usuario_id = usuarios_map.get(nombre_usuario)
        
        if producto_id and proveedor_id and usuario_id:
            cursor.execute(
                """INSERT INTO AsignadorCompra 
                   (Fecha_Compra, Producto, Proveedor, Fin_Garantia, Comprado_Para, NumeroSerie) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (fecha, producto_id, proveedor_id, fin_garantia, usuario_id, numero_serie)
            )
            compras_insertadas += 1
        else:
            print(f"⚠️  Datos faltantes: Prod={nombre_producto}({producto_id}), Prov={nombre_proveedor}({proveedor_id}), User={nombre_usuario}({usuario_id})")
    
    print(f"✅ {compras_insertadas} compras insertadas")

def insertar_mantenimientos(cursor):
    """Insertar mantenimientos de ejemplo"""
    cursor.execute("SELECT IdAsignadorCompra, NumeroSerie FROM AsignadorCompra")
    compras_map = {numero: id for id, numero in cursor.fetchall()}
    
    mantenimientos = [
        ('SN001', 'Pantalla con rayones', date(2024, 3, 5), 'Se rayó la pantalla', 'Cambio de pantalla', date(2024, 3, 7)),
        ('SN002', 'No enciende', date(2024, 4, 10), 'Problema de fuente de poder', 'Reemplazo de fuente', date(2024, 4, 12)),
        ('SN003', 'Silla inestable', date(2024, 5, 15), 'Tornillos flojos', 'Ajuste general', date(2024, 5, 15)),
        ('SN005', 'Atasco de papel', date(2024, 6, 20), 'Papel atorado en rodillos', 'Limpieza interna', date(2024, 6, 21)),
        ('SN007', 'Batería no carga', date(2024, 7, 25), None, 'Reemplazo de batería', date(2024, 7, 26))
    ]
    
    mantenimientos_insertados = 0
    for numero_serie, problema, fecha_inicio, observaciones, diagnostico, fecha_final in mantenimientos:
        compra_id = compras_map.get(numero_serie)
        if compra_id:
            cursor.execute(
                """INSERT INTO Mantenimientos 
                   (Compra, Problema_Presentado, Fecha_Inicio, Observaciones, Diagnostico, Fecha_Final) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (compra_id, problema, fecha_inicio, observaciones, diagnostico, fecha_final)
            )
            mantenimientos_insertados += 1
        else:
            print(f"⚠️  Compra '{numero_serie}' no encontrada")
    
    print(f"✅ {mantenimientos_insertados} mantenimientos insertados")

def insertar_relaciones(cursor):
    """Insertar relaciones entre compras de ejemplo"""
    cursor.execute("SELECT IdAsignadorCompra, NumeroSerie FROM AsignadorCompra")
    compras_map = {numero: id for id, numero in cursor.fetchall()}
    
    relaciones = [
        ('SN001', 'SN011'),  # Laptop con RAM
        ('SN001', 'SN012'),  # Laptop con SSD
        ('SN002', 'SN013'),  # Computadora con Monitor
        ('SN001', 'SN013'),  # Laptop con Monitor (también)
        ('SN003', 'SN004'),  # Silla con Escritorio
        ('SN007', 'SN008')   # Impresora con Tóner
    ]
    
    relaciones_insertadas = 0
    for num_madre, num_hijo in relaciones:
        id_madre = compras_map.get(num_madre)
        id_hijo = compras_map.get(num_hijo)
        
        if id_madre and id_hijo:
            # Verificar que no exista ya
            cursor.execute(
                "SELECT 1 FROM Relacion_Entre_Compras WHERE IdCompra_Madre = %s AND IdSub_Compra = %s",
                (id_madre, id_hijo)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO Relacion_Entre_Compras (IdCompra_Madre, IdSub_Compra) VALUES (%s, %s)",
                    (id_madre, id_hijo)
                )
                relaciones_insertadas += 1
        else:
            print(f"⚠️  Compras no encontradas: {num_madre}({id_madre}) -> {num_hijo}({id_hijo})")
    
    print(f"✅ {relaciones_insertadas} relaciones insertadas")

def main():
    """Función principal"""
    print("=" * 60)
    print("🌱 SEED MEJORADO - INICIANDO")
    print("=" * 60)
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    try:
        # Reiniciar completamente
        reiniciar_base_datos(cursor)
        
        # Insertar datos
        insertar_categorias(cursor)
        insertar_proveedores(cursor)
        insertar_ubicaciones(cursor)
        insertar_usuarios(cursor)
        insertar_productos(cursor)
        insertar_compras(cursor)
        insertar_mantenimientos(cursor)
        insertar_relaciones(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("🎉 SEED COMPLETADO EXITOSAMENTE!")
        print("=" * 60)
        
        # Resumen detallado
        cursor.execute("""
            SELECT 'Categorías' as tipo, COUNT(*) as cantidad FROM Categorias
            UNION ALL SELECT 'Productos', COUNT(*) FROM Productos
            UNION ALL SELECT '  - Madre', COUNT(*) FROM Productos WHERE Es_Producto_Madre = TRUE
            UNION ALL SELECT '  - Hijo', COUNT(*) FROM Productos WHERE Es_Producto_Madre = FALSE
            UNION ALL SELECT 'Proveedores', COUNT(*) FROM Proveedores
            UNION ALL SELECT 'Ubicaciones', COUNT(*) FROM Ubicaciones
            UNION ALL SELECT 'Usuarios', COUNT(*) FROM Usuarios
            UNION ALL SELECT 'Compras', COUNT(*) FROM AsignadorCompra
            UNION ALL SELECT 'Mantenimientos', COUNT(*) FROM Mantenimientos
            UNION ALL SELECT 'Relaciones', COUNT(*) FROM Relacion_Entre_Compras
        """)
        
        for row in cursor.fetchall():
            print(f"📊 {row[0]}: {row[1]}")
        
        print("=" * 60)
        print("✅ Base de datos lista!")
        print("🌐 Accede a: http://localhost:5000")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()