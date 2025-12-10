import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-docker')

# ========== CONEXIÓN A LA BASE DE DATOS ==========
def get_db_connection():
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/inventario')
    
    print(f"🔗 Intentando conectar a: {database_url}")
    
    try:
        conn = psycopg2.connect(database_url)
        print("✅ Conexión exitosa a PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        raise

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """Ejecutar consulta SQL"""
    conn = get_db_connection()
    if not conn:
        print("❌ No hay conexión a la BD")
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            
            if fetchone:
                result = cursor.fetchone()
                conn.commit()
            elif fetchall:
                result = cursor.fetchall()
                conn.commit()
            else:
                # Para INSERT, UPDATE, DELETE
                result = cursor.rowcount
                conn.commit()
        
        conn.close()
        return result
    except Exception as e:
        print(f"❌ Error en consulta: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return None

# ========== RUTAS PRINCIPALES ==========
@app.route('/')
def index():
    """Página de inicio con estadísticas del sistema"""
    try:
        # Verificar conexión a la BD
        conn = get_db_connection()
        conn.close()
        db_status = "Conectada"
        
        # Obtener estadísticas
        stats = {
            'productos': execute_query("SELECT COUNT(*) as count FROM Productos", fetchone=True)['count'],
            'compras': execute_query("SELECT COUNT(*) as count FROM AsignadorCompra", fetchone=True)['count'],
            'usuarios': execute_query("SELECT COUNT(*) as count FROM Usuarios", fetchone=True)['count'],
            'mantenimientos': execute_query("SELECT COUNT(*) as count FROM Mantenimientos", fetchone=True)['count'],
        }
    except Exception:
        db_status = "Error de Conexión"
        stats = {
            'productos': 'N/A',
            'compras': 'N/A',
            'usuarios': 'N/A',
            'mantenimientos': 'N/A',
        }
        
    return render_template('index.html', db_status=db_status, stats=stats)


@app.route('/health')
def health():
    return jsonify(status="ok")

# ========== CRUD PARA CATEGORÍAS ==========
@app.route('/categorias')
def categorias():
    """Listar categorías con ordenamiento"""
    # --- Lógica de Ordenamiento ---
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')

    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    
    # La única columna para ordenar es Nombre_Categoria
    order_by_clause = f"ORDER BY Nombre_Categoria {sort_order.upper()}"

    # --- Consultas a la BD ---
    categorias_list = execute_query(
        f"SELECT IdCategoria as id, Nombre_Categoria as nombre FROM Categorias {order_by_clause}", 
        fetchall=True
    )
    
    editar_id = request.args.get('editar')
    categoria_edit = None
    if editar_id:
        categoria_edit = execute_query(
            "SELECT IdCategoria as id, Nombre_Categoria as nombre FROM Categorias WHERE IdCategoria = %s", 
            (editar_id,), 
            fetchone=True
        )

    return render_template('categorias.html', 
                         categorias=categorias_list or [],
                         categoria_edit=categoria_edit,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/categorias/agregar', methods=['POST'])
def agregar_categoria():
    """Agregar nueva categoría"""
    nombre = request.form.get('nombre_categoria', '').strip()
    if nombre:
        execute_query("INSERT INTO Categorias (Nombre_Categoria) VALUES (%s)", (nombre,))
        flash('✅ Categoría agregada exitosamente', 'success')
    return redirect(url_for('categorias'))

@app.route('/categorias/editar/<int:id>', methods=['POST'])
def editar_categoria(id):
    """Editar categoría existente"""
    nombre = request.form.get('nombre_categoria', '').strip()
    if nombre:
        execute_query(
            "UPDATE Categorias SET Nombre_Categoria = %s WHERE IdCategoria = %s",
            (nombre, id)
        )
        flash('✅ Categoría actualizada exitosamente', 'success')
    return redirect(url_for('categorias'))

@app.route('/categorias/eliminar/<int:id>')
def eliminar_categoria(id):
    """Eliminar categoría"""
    execute_query("DELETE FROM Categorias WHERE IdCategoria = %s", (id,))
    flash('✅ Categoría eliminada exitosamente', 'success')
    return redirect(url_for('categorias'))

# ========== CRUD PARA PRODUCTOS ==========
@app.route('/productos')
def productos():
    """Listar productos con filtros y ordenamiento"""
    # --- Lógica de Ordenamiento ---
    sort_by = request.args.get('sort_by', 'es_madre')
    sort_order = request.args.get('sort_order', 'desc')

    sort_columns_map = {
        'nombre': "p.Nombre",
        'categoria_nombre': "c.Nombre_Categoria",
        'es_madre': "p.Es_Producto_Madre"
    }
    
    sort_column = sort_columns_map.get(sort_by, "p.Es_Producto_Madre")
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'desc'
    
    # Ordenar por tipo y luego por nombre como secundario
    order_by_clause = f"ORDER BY {sort_column} {sort_order.upper()}, p.Nombre ASC"

    # --- Consultas a la BD ---
    productos_list = execute_query(f"""
        SELECT p.IdProducto as id, p.Nombre as nombre, 
               p.Categoria as categoria_id,
               p.Es_Producto_Madre as es_madre,
               c.Nombre_Categoria as categoria_nombre
        FROM Productos p
        LEFT JOIN Categorias c ON p.Categoria = c.IdCategoria
        {order_by_clause}
    """, fetchall=True)
    
    categorias_list = execute_query(
        "SELECT IdCategoria as id, Nombre_Categoria as nombre FROM Categorias ORDER BY Nombre_Categoria", 
        fetchall=True
    )
    
    editar_id = request.args.get('editar')
    producto_edit = None
    if editar_id:
        producto_edit = execute_query(
            "SELECT IdProducto as id, Nombre as nombre, Categoria as categoria_id, Es_Producto_Madre as es_madre FROM Productos WHERE IdProducto = %s", 
            (editar_id,), 
            fetchone=True
        )
    
    return render_template('productos.html', 
                         productos=productos_list or [],
                         categorias=categorias_list or [],
                         producto_edit=producto_edit,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/productos/agregar', methods=['POST'])
def agregar_producto():
    """Agregar nuevo producto"""
    nombre = request.form.get('nombre', '').strip()
    categoria = request.form.get('categoria', '')
    es_madre = request.form.get('es_madre') == 'true'  # Convertir a booleano
    
    if nombre and categoria:
        execute_query(
            "INSERT INTO Productos (Nombre, Categoria, Es_Producto_Madre) VALUES (%s, %s, %s)",
            (nombre, categoria, es_madre)
        )
        flash('✅ Producto agregado exitosamente', 'success')
    
    return redirect(url_for('productos'))

@app.route('/productos/editar/<int:id>', methods=['POST'])
def editar_producto(id):
    """Editar producto existente"""
    nombre = request.form.get('nombre', '').strip()
    categoria = request.form.get('categoria', '')
    es_madre = request.form.get('es_madre') == 'true'
    
    if nombre and categoria:
        execute_query(
            "UPDATE Productos SET Nombre = %s, Categoria = %s, Es_Producto_Madre = %s WHERE IdProducto = %s",
            (nombre, categoria, es_madre, id)
        )
        flash('✅ Producto actualizado exitosamente', 'success')
    
    return redirect(url_for('productos'))

@app.route('/productos/eliminar/<int:id>')
def eliminar_producto(id):
    """Eliminar producto"""
    # Primero verificar si el producto está siendo usado en compras
    compras_con_producto = execute_query(
        "SELECT COUNT(*) as count FROM AsignadorCompra WHERE Producto = %s",
        (id,), fetchone=True
    )
    
    if compras_con_producto and compras_con_producto['count'] > 0:
        flash('❌ No se puede eliminar el producto porque está siendo usado en compras', 'error')
        return redirect(url_for('productos'))
    
    # Si no está siendo usado, eliminar
    execute_query("DELETE FROM Productos WHERE IdProducto = %s", (id,))
    flash('✅ Producto eliminado exitosamente', 'success')
    return redirect(url_for('productos'))

# ========== CRUD PARA PROVEEDORES ==========
@app.route('/proveedores')
def proveedores():
    """Listar proveedores con ordenamiento"""
    # --- Lógica de Ordenamiento ---
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')

    # Validar que el orden sea 'asc' o 'desc'
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    
    # Para proveedores, solo podemos ordenar por nombre
    order_by_clause = f"ORDER BY Nombre {sort_order.upper()}"

    # --- Consultas a la BD ---
    proveedores_list = execute_query(
        f"SELECT IdProveedor as id, Nombre as nombre FROM Proveedores {order_by_clause}", 
        fetchall=True
    )
    
    editar_id = request.args.get('editar')
    proveedor_edit = None
    if editar_id:
        proveedor_edit = execute_query(
            "SELECT IdProveedor as id, Nombre as nombre FROM Proveedores WHERE IdProveedor = %s", 
            (editar_id,), 
            fetchone=True
        )

    return render_template('proveedores.html', 
                         proveedores=proveedores_list or [],
                         proveedor_edit=proveedor_edit,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/proveedores/agregar', methods=['POST'])
def agregar_proveedor():
    """Agregar nuevo proveedor"""
    nombre = request.form.get('nombre', '').strip()
    if nombre:
        execute_query("INSERT INTO Proveedores (Nombre) VALUES (%s)", (nombre,))
        flash('✅ Proveedor agregado exitosamente', 'success')
    return redirect(url_for('proveedores'))

@app.route('/proveedores/editar/<int:id>', methods=['POST'])
def editar_proveedor(id):
    """Editar proveedor existente"""
    nombre = request.form.get('nombre', '').strip()
    if nombre:
        execute_query(
            "UPDATE Proveedores SET Nombre = %s WHERE IdProveedor = %s",
            (nombre, id)
        )
        flash('✅ Proveedor actualizado exitosamente', 'success')
    return redirect(url_for('proveedores'))

@app.route('/proveedores/eliminar/<int:id>')
def eliminar_proveedor(id):
    """Eliminar proveedor"""
    execute_query("DELETE FROM Proveedores WHERE IdProveedor = %s", (id,))
    flash('✅ Proveedor eliminado exitosamente', 'success')
    return redirect(url_for('proveedores'))

# ========== CRUD PARA UBICACIONES ==========
@app.route('/ubicaciones')
def ubicaciones():
    """Listar ubicaciones con ordenamiento"""
    # --- Lógica de Ordenamiento ---
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')

    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    
    # La única columna para ordenar es NombreEdificio
    order_by_clause = f"ORDER BY NombreEdificio {sort_order.upper()}"

    # --- Consultas a la BD ---
    ubicaciones_list = execute_query(
        f"SELECT IdUbicacion as id, NombreEdificio as nombre FROM Ubicaciones {order_by_clause}", 
        fetchall=True
    )
    
    editar_id = request.args.get('editar')
    ubicacion_edit = None
    if editar_id:
        ubicacion_edit = execute_query(
            "SELECT IdUbicacion as id, NombreEdificio as nombre FROM Ubicaciones WHERE IdUbicacion = %s", 
            (editar_id,), 
            fetchone=True
        )

    return render_template('ubicaciones.html', 
                         ubicaciones=ubicaciones_list or [],
                         ubicacion_edit=ubicacion_edit,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/ubicaciones/agregar', methods=['POST'])
def agregar_ubicacion():
    """Agregar nueva ubicación"""
    nombre = request.form.get('nombre_edificio', '').strip()
    if nombre:
        execute_query("INSERT INTO Ubicaciones (NombreEdificio) VALUES (%s)", (nombre,))
        flash('✅ Ubicación agregada exitosamente', 'success')
    return redirect(url_for('ubicaciones'))

@app.route('/ubicaciones/editar/<int:id>', methods=['POST'])
def editar_ubicacion(id):
    """Editar ubicación existente"""
    nombre = request.form.get('nombre_edificio', '').strip()
    if nombre:
        execute_query(
            "UPDATE Ubicaciones SET NombreEdificio = %s WHERE IdUbicacion = %s",
            (nombre, id)
        )
        flash('✅ Ubicación actualizada exitosamente', 'success')
    return redirect(url_for('ubicaciones'))

@app.route('/ubicaciones/eliminar/<int:id>')
def eliminar_ubicacion(id):
    """Eliminar ubicación"""
    execute_query("DELETE FROM Ubicaciones WHERE IdUbicacion = %s", (id,))
    flash('✅ Ubicación eliminada exitosamente', 'success')
    return redirect(url_for('ubicaciones'))

# ========== CRUD PARA USUARIOS ==========
@app.route('/usuarios')
def usuarios():
    """Listar usuarios con filtros y ordenamiento"""
    # --- Lógica de Ordenamiento ---
    sort_by = request.args.get('sort_by', 'nombre')
    sort_order = request.args.get('sort_order', 'asc')

    sort_columns_map = {
        'nombre': "u.Nombre",
        'ubicacion_nombre': "ub.NombreEdificio",
        'ubicacion_especifica': "u.Ubicacion_Especifica"
    }
    
    sort_column = sort_columns_map.get(sort_by, "u.Nombre")
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    
    order_by_clause = f"ORDER BY {sort_column} {sort_order.upper()}"

    # --- Consultas a la BD ---
    usuarios_list = execute_query(f"""
        SELECT u.IdUsuario as id, 
               u.Nombre as nombre, 
               u.Ubicacion_Especifica as ubicacion_especifica, 
               ub.NombreEdificio as ubicacion_nombre,
               u.Ubicacion as ubicacion_id
        FROM Usuarios u
        LEFT JOIN Ubicaciones ub ON u.Ubicacion = ub.IdUbicacion
        {order_by_clause}
    """, fetchall=True)
    
    ubicaciones_list = execute_query(
        "SELECT IdUbicacion as id, NombreEdificio as nombre FROM Ubicaciones ORDER BY NombreEdificio", 
        fetchall=True
    )
    
    editar_id = request.args.get('editar')
    usuario_edit = None
    if editar_id:
        usuario_edit = execute_query(
            "SELECT IdUsuario as id, Nombre as nombre, Ubicacion as ubicacion_id, Ubicacion_Especifica as ubicacion_especifica FROM Usuarios WHERE IdUsuario = %s", 
            (editar_id,), 
            fetchone=True
        )

    return render_template('usuarios.html', 
                         usuarios=usuarios_list or [],
                         ubicaciones=ubicaciones_list or [],
                         usuario_edit=usuario_edit,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/usuarios/agregar', methods=['POST'])
def agregar_usuario():
    """Agregar nuevo usuario"""
    nombre = request.form.get('nombre', '').strip()
    ubicacion = request.form.get('ubicacion', '')
    ubicacion_especifica = request.form.get('ubicacion_especifica', '').strip()
    
    if nombre and ubicacion:
        execute_query(
            "INSERT INTO Usuarios (Nombre, Ubicacion, Ubicacion_Especifica) VALUES (%s, %s, %s)",
            (nombre, ubicacion, ubicacion_especifica)
        )
        flash('✅ Usuario agregado exitosamente', 'success')
    
    return redirect(url_for('usuarios'))

@app.route('/usuarios/editar/<int:id>', methods=['POST'])
def editar_usuario(id):
    """Editar usuario existente"""
    nombre = request.form.get('nombre', '').strip()
    ubicacion = request.form.get('ubicacion', '')
    ubicacion_especifica = request.form.get('ubicacion_especifica', '').strip()
    
    if nombre and ubicacion:
        execute_query(
            "UPDATE Usuarios SET Nombre = %s, Ubicacion = %s, Ubicacion_Especifica = %s WHERE IdUsuario = %s",
            (nombre, ubicacion, ubicacion_especifica, id)
        )
        flash('✅ Usuario actualizado exitosamente', 'success')
    
    return redirect(url_for('usuarios'))

@app.route('/usuarios/eliminar/<int:id>')
def eliminar_usuario(id):
    """Eliminar usuario"""
    execute_query("DELETE FROM Usuarios WHERE IdUsuario = %s", (id,))
    flash('✅ Usuario eliminado exitosamente', 'success')
    return redirect(url_for('usuarios'))

# ========== CRUD PARA COMPRAS ==========
@app.route('/compras')
def compras():
    """Listar compras con filtros y ordenamiento"""
    # --- Lógica de Ordenamiento ---
    sort_by = request.args.get('sort_by', 'fecha_compra')
    sort_order = request.args.get('sort_order', 'desc')

    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'desc'
    
    order_by_clause = f"ORDER BY ac.Fecha_Compra {sort_order.upper()}"

    # --- Consultas a la BD ---
    compras_list = execute_query(f"""
        SELECT ac.IdAsignadorCompra as id,
               ac.Fecha_Compra as fecha_compra,
               p.Nombre as producto_nombre,
               pr.Nombre as proveedor_nombre,
               u.Nombre as usuario_nombre,
               ub.NombreEdificio as ubicacion_nombre,
               ac.NumeroSerie as numero_serie,
               ac.Fin_Garantia as fin_garantia,
               ac.Producto as producto_id,
               ac.Proveedor as proveedor_id,
               ac.Comprado_Para as usuario_id
        FROM AsignadorCompra ac
        LEFT JOIN Productos p ON ac.Producto = p.IdProducto
        LEFT JOIN Proveedores pr ON ac.Proveedor = pr.IdProveedor
        LEFT JOIN Usuarios u ON ac.Comprado_Para = u.IdUsuario
        LEFT JOIN Ubicaciones ub ON u.Ubicacion = ub.IdUbicacion
        {order_by_clause}
    """, fetchall=True)
    
    productos_list = execute_query(
        """SELECT IdProducto as id, Nombre as nombre, Categoria as categoria_id,
                  Es_Producto_Madre as es_madre, c.Nombre_Categoria as categoria_nombre
           FROM Productos p
           LEFT JOIN Categorias c ON p.Categoria = c.IdCategoria
           ORDER BY Nombre""", 
        fetchall=True
    )
    
    proveedores_list = execute_query(
        "SELECT IdProveedor as id, Nombre as nombre FROM Proveedores ORDER BY Nombre", 
        fetchall=True
    )
    
    usuarios_list = execute_query("""
        SELECT u.IdUsuario as id, u.Nombre as nombre, ub.NombreEdificio as ubicacion_nombre
        FROM Usuarios u
        LEFT JOIN Ubicaciones ub ON u.Ubicacion = ub.IdUbicacion
        ORDER BY u.Nombre
    """, fetchall=True)
    
    ubicaciones_list = execute_query(
        "SELECT IdUbicacion as id, NombreEdificio as nombre FROM Ubicaciones ORDER BY NombreEdificio",
        fetchall=True
    )

    # Obtener compras MADRE (para vincular como padre)
    # Estas son compras ya registradas donde el producto es de tipo "Madre" y tienen usuario asignado
    compras_madre_list = execute_query("""
        SELECT ac.IdAsignadorCompra as id,
               ac.NumeroSerie as numero_serie,
               p.Nombre as nombre,
               ac.Comprado_Para as usuario_id,
               u.Nombre as usuario_nombre,
               p.Es_Producto_Madre as es_madre
        FROM AsignadorCompra ac
        INNER JOIN Productos p ON ac.Producto = p.IdProducto
        LEFT JOIN Usuarios u ON ac.Comprado_Para = u.IdUsuario
        WHERE p.Es_Producto_Madre = TRUE
          AND ac.Comprado_Para IS NOT NULL
        ORDER BY u.Nombre, p.Nombre
    """, fetchall=True)
    
    # Debug: Imprimir los datos obtenidos
    print("\n" + "="*60)
    print("🔍 DEBUG - Compras Madre obtenidas para vincular:")
    print("="*60)
    if compras_madre_list:
        for cm in compras_madre_list:
            print(f"  ID Compra: {cm.get('id')}")
            print(f"  Usuario ID: {cm.get('usuario_id')} (tipo: {type(cm.get('usuario_id'))})")
            print(f"  Usuario Nombre: {cm.get('usuario_nombre')}")
            print(f"  Producto: {cm.get('nombre')}")
            print(f"  Es Madre: {cm.get('es_madre')}")
            print(f"  Serie: {cm.get('numero_serie')}")
            print(f"  {'-'*58}")
        print(f"Total: {len(compras_madre_list)} compras madre encontradas")
    else:
        print("  ⚠️ No se encontraron compras madre")
        print("  💡 Verifica que:")
        print("     1. Existan compras en la tabla AsignadorCompra")
        print("     2. Los productos tengan Es_Producto_Madre = TRUE")
        print("     3. Las compras tengan un usuario asignado (Comprado_Para)")
    print("="*60 + "\n")
    
    editar_id = request.args.get('editar')
    compra_edit = None
    if editar_id:
        compra_edit = execute_query(
            """SELECT IdAsignadorCompra as id, Fecha_Compra as fecha_compra, 
                      Producto as producto_id, Proveedor as proveedor_id, 
                      Fin_Garantia as fin_garantia, Comprado_Para as usuario_id, 
                      NumeroSerie as numero_serie 
               FROM AsignadorCompra WHERE IdAsignadorCompra = %s""", 
            (editar_id,), 
            fetchone=True
        )

    return render_template('compras.html', 
                         compras=compras_list or [],
                         productos=productos_list or [],
                         proveedores=proveedores_list or [],
                         usuarios=usuarios_list or [],
                         ubicaciones=ubicaciones_list or [],
                         compras_madre=compras_madre_list or [],
                         compra_edit=compra_edit,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/compras/agregar', methods=['POST'])
def agregar_compra():
    """Agregar una o múltiples compras"""
    # Procesar múltiples compras desde la tabla
    fechas = request.form.getlist('fecha_compra[]')
    productos = request.form.getlist('producto[]')
    proveedores = request.form.getlist('proveedor[]')
    fin_garantias = request.form.getlist('fin_garantia[]')
    usuarios = request.form.getlist('comprado_para[]')
    series = request.form.getlist('numero_serie[]')
    productos_padre = request.form.getlist('producto_padre[]')
    
    count_exitosas = 0
    errors = []
    
    for i in range(len(fechas)):
        fecha = fechas[i].strip() if i < len(fechas) else None
        producto = productos[i].strip() if i < len(productos) else None
        proveedor = proveedores[i].strip() if i < len(proveedores) else None
        fin_garantia = fin_garantias[i].strip() if (i < len(fin_garantias) and fin_garantias[i]) else None
        usuario = usuarios[i].strip() if (i < len(usuarios) and usuarios[i]) else None
        serie = series[i].strip() if (i < len(series) and series[i]) else ''
        producto_padre_id = productos_padre[i].strip() if (i < len(productos_padre) and productos_padre[i]) else None
        
        # Validar campos requeridos
        if not fecha or not producto or not proveedor:
            errors.append(f"Fila {i+1}: Faltan campos requeridos (Fecha, Producto o Proveedor)")
            continue
        
        try:
            # Insertar compra
            result = execute_query(
                """INSERT INTO AsignadorCompra 
                   (Fecha_Compra, Producto, Proveedor, Fin_Garantia, Comprado_Para, NumeroSerie) 
                   VALUES (%s, %s, %s, %s, %s, %s)
                   RETURNING IdAsignadorCompra""",
                (fecha, int(producto), int(proveedor), fin_garantia, int(usuario) if usuario else None, serie),
                fetchone=True
            )
            
            if result:
                # Obtener el ID de la compra insertada
                compra_id = result.get('idasignadorcompra') or result.get('IdAsignadorCompra')
                if compra_id:
                    count_exitosas += 1
                    
                    # Si se especificó un producto padre, crear la relación
                    if producto_padre_id:
                        try:
                            execute_query(
                                "INSERT INTO Relacion_Entre_Compras (IdCompra_Madre, IdSub_Compra) VALUES (%s, %s)",
                                (int(producto_padre_id), compra_id)
                            )
                            print(f"✅ Relación creada: {producto_padre_id} -> {compra_id}")
                        except Exception as e:
                            print(f"⚠️ No se pudo crear la relación: {e}")
                else:
                    errors.append(f"Fila {i+1}: No se obtuvo ID de la compra")
            else:
                errors.append(f"Fila {i+1}: Error al insertar en la BD")
        except Exception as e:
            errors.append(f"Fila {i+1}: Error - {str(e)}")
            print(f"❌ Error insertando compra en fila {i+1}: {e}")
    
    # Mostrar mensajes
    if count_exitosas > 0:
        flash(f'✅ {count_exitosas} compra(s) agregada(s) exitosamente', 'success')
    
    if errors:
        for error in errors:
            flash(f'⚠️ {error}', 'warning')
    
    if count_exitosas == 0 and not errors:
        flash('❌ No se pudo agregar ninguna compra. Verifica que todos los campos requeridos estén completos.', 'error')
    
    return redirect(url_for('compras'))

@app.route('/compras/editar/<int:id>', methods=['POST'])
def editar_compra(id):
    """Editar compra existente"""
    fecha_compra = request.form.get('fecha_compra')
    producto = request.form.get('producto')
    proveedor = request.form.get('proveedor')
    fin_garantia = request.form.get('fin_garantia') or None
    comprado_para = request.form.get('comprado_para') or None
    numero_serie = request.form.get('numero_serie', '').strip()
    
    if fecha_compra and producto and proveedor:
        execute_query(
            """UPDATE AsignadorCompra 
               SET Fecha_Compra = %s, Producto = %s, Proveedor = %s, 
                   Fin_Garantia = %s, Comprado_Para = %s, NumeroSerie = %s 
               WHERE IdAsignadorCompra = %s""",
            (fecha_compra, producto, proveedor, fin_garantia, comprado_para, numero_serie, id)
        )
        flash('✅ Compra actualizada exitosamente', 'success')
    
    return redirect(url_for('compras'))

@app.route('/compras/eliminar/<int:id>')
def eliminar_compra(id):
    """Eliminar compra"""
    execute_query("DELETE FROM AsignadorCompra WHERE IdAsignadorCompra = %s", (id,))
    flash('✅ Compra eliminada exitosamente', 'success')
    return redirect(url_for('compras'))

# ========== CRUD PARA MANTENIMIENTOS ==========
@app.route('/mantenimientos')
def mantenimientos():
    """Listar mantenimientos con filtros y ordenamiento"""
    # --- Lógica de Ordenamiento ---
    sort_by = request.args.get('sort_by', 'fecha_inicio')
    sort_order = request.args.get('sort_order', 'desc')

    # Mapeo seguro de columnas para evitar inyección SQL
    sort_columns_map = {
        'producto_nombre': "p.Nombre",
        'usuario_nombre': "u.Nombre",
        'ubicacion_nombre': "ub.NombreEdificio",
        'problema': "m.Problema_Presentado",
        'fecha_inicio': "m.Fecha_Inicio",
        'fecha_final': "m.Fecha_Final"
    }
    
    # Validar que la columna de ordenamiento sea válida, si no, usar una por defecto
    sort_column = sort_columns_map.get(sort_by, "m.Fecha_Inicio")
    # Validar que el orden sea 'asc' o 'desc'
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'desc'

    # Construir la cláusula ORDER BY
    order_by_clause = f"ORDER BY COALESCE({sort_column}, '1970-01-01'::date) {sort_order.upper()}"

    # --- Consultas a la BD ---
    mantenimientos_list = execute_query(f"""
        SELECT m.IdMantenimiento as id, 
               m.Problema_Presentado as problema,
               TO_CHAR(m.Fecha_Inicio, 'YYYY-MM-DD') as fecha_inicio,
               TO_CHAR(m.Fecha_Final, 'YYYY-MM-DD') as fecha_final,
               m.Observaciones as observaciones, 
               m.Diagnostico as diagnostico,
               ac.NumeroSerie as numero_serie,
               p.Nombre as producto_nombre,
               u.Nombre as usuario_nombre,
               ub.NombreEdificio as ubicacion_nombre,
               m.Compra as compra_id
        FROM Mantenimientos m
        LEFT JOIN AsignadorCompra ac ON m.Compra = ac.IdAsignadorCompra
        LEFT JOIN Productos p ON ac.Producto = p.IdProducto
        LEFT JOIN Usuarios u ON ac.Comprado_Para = u.IdUsuario
        LEFT JOIN Ubicaciones ub ON u.Ubicacion = ub.IdUbicacion
        {order_by_clause}
    """, fetchall=True)
    
    compras_list = execute_query("""
        SELECT ac.IdAsignadorCompra as id, 
               ac.NumeroSerie as numero_serie, 
               p.Nombre as nombre,
               u.IdUsuario as usuario_id,
               u.Nombre as usuario_nombre,
               ub.IdUbicacion as ubicacion_id,
               ub.NombreEdificio as ubicacion_nombre,
               ac.Fecha_Compra as fecha_compra
        FROM AsignadorCompra ac
        LEFT JOIN Productos p ON ac.Producto = p.IdProducto
        LEFT JOIN Usuarios u ON ac.Comprado_Para = u.IdUsuario
        LEFT JOIN Ubicaciones ub ON u.Ubicacion = ub.IdUbicacion
        WHERE ac.NumeroSerie IS NOT NULL AND ac.NumeroSerie != ''
        ORDER BY ub.NombreEdificio, u.Nombre, p.Nombre
    """, fetchall=True)
    
    ubicaciones_list = execute_query("SELECT IdUbicacion as id, NombreEdificio as nombre FROM Ubicaciones ORDER BY NombreEdificio", fetchall=True)
    usuarios_list = execute_query("SELECT IdUsuario as id, Nombre as nombre FROM Usuarios ORDER BY Nombre", fetchall=True)
    
    editar_id = request.args.get('editar')
    mantenimiento_edit = None
    if editar_id:
        mantenimiento_edit = execute_query(
            "SELECT IdMantenimiento as id, Compra as compra_id, Problema_Presentado as problema, TO_CHAR(Fecha_Inicio, 'YYYY-MM-DD') as fecha_inicio, Observaciones as observaciones, Diagnostico as diagnostico, TO_CHAR(Fecha_Final, 'YYYY-MM-DD') as fecha_final FROM Mantenimientos WHERE IdMantenimiento = %s", 
            (editar_id,), 
            fetchone=True
        )
    
    return render_template('mantenimientos.html', 
                         mantenimientos=mantenimientos_list or [],
                         compras=compras_list or [],
                         ubicaciones=ubicaciones_list or [],
                         usuarios=usuarios_list or [],
                         mantenimiento_edit=mantenimiento_edit,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/mantenimientos/agregar', methods=['POST'])
def agregar_mantenimiento():
    """Agregar nuevo mantenimiento"""
    compra = request.form.get('compra')
    problema = request.form.get('problema_presentado', '').strip()
    diagnostico = request.form.get('diagnostico', '').strip()
    fecha_inicio = request.form.get('fecha_inicio') or None
    fecha_final = request.form.get('fecha_final') or None
    observaciones = request.form.get('observaciones', '').strip()

    if compra and problema:
        execute_query(
            """INSERT INTO Mantenimientos 
               (Compra, Problema_Presentado, Diagnostico, Fecha_Inicio, Fecha_Final, Observaciones) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (compra, problema, diagnostico, fecha_inicio, fecha_final, observaciones)
        )
        flash('✅ Mantenimiento agregado exitosamente', 'success')
    else:
        flash('❌ Faltan campos requeridos (Compra y Problema)', 'error')
    
    return redirect(url_for('mantenimientos'))

@app.route('/mantenimientos/editar/<int:id>', methods=['POST'])
def editar_mantenimiento(id):
    """Editar mantenimiento existente"""
    compra = request.form.get('compra')
    problema = request.form.get('problema_presentado', '').strip()
    diagnostico = request.form.get('diagnostico', '').strip()
    fecha_inicio = request.form.get('fecha_inicio') or None
    fecha_final = request.form.get('fecha_final') or None
    observaciones = request.form.get('observaciones', '').strip()

    if compra and problema:
        execute_query(
            """UPDATE Mantenimientos 
               SET Compra = %s, Problema_Presentado = %s, Diagnostico = %s, 
                   Fecha_Inicio = %s, Fecha_Final = %s, Observaciones = %s
               WHERE IdMantenimiento = %s""",
            (compra, problema, diagnostico, fecha_inicio, fecha_final, observaciones, id)
        )
        flash('✅ Mantenimiento actualizado exitosamente', 'success')
    else:
        flash('❌ Faltan campos requeridos (Compra y Problema)', 'error')

    return redirect(url_for('mantenimientos'))

@app.route('/mantenimientos/eliminar/<int:id>')
def eliminar_mantenimiento(id):
    """Eliminar mantenimiento"""
    execute_query("DELETE FROM Mantenimientos WHERE IdMantenimiento = %s", (id,))
    flash('✅ Mantenimiento eliminado exitosamente', 'success')
    return redirect(url_for('mantenimientos'))


# ========== CRUD PARA RELACIONES ENTRE COMPRAS ==========
@app.route('/relaciones')
def relaciones():
    """Listar relaciones entre compras"""
    relaciones_list = execute_query("""
        SELECT rec.IdRelacion_Entre_Compras as id, 
               rec.IdCompra_Madre as compra_madre_id, 
               rec.IdSub_Compra as sub_compra_id,
               ac1.NumeroSerie as serie_madre,
               ac2.NumeroSerie as serie_hija,
               p1.Nombre as producto_madre_nombre,
               p2.Nombre as producto_hija_nombre,
               p1.Es_Producto_Madre as producto_madre_es_madre,
               p2.Es_Producto_Madre as producto_hija_es_madre,
               u1.Nombre as usuario_madre_nombre,
               u2.Nombre as usuario_hija_nombre,
               ub1.NombreEdificio as ubicacion_madre,
               ub2.NombreEdificio as ubicacion_hija
        FROM Relacion_Entre_Compras rec
        LEFT JOIN AsignadorCompra ac1 ON rec.IdCompra_Madre = ac1.IdAsignadorCompra
        LEFT JOIN AsignadorCompra ac2 ON rec.IdSub_Compra = ac2.IdAsignadorCompra
        LEFT JOIN Productos p1 ON ac1.Producto = p1.IdProducto
        LEFT JOIN Productos p2 ON ac2.Producto = p2.IdProducto
        LEFT JOIN Usuarios u1 ON ac1.Comprado_Para = u1.IdUsuario
        LEFT JOIN Usuarios u2 ON ac2.Comprado_Para = u2.IdUsuario
        LEFT JOIN Ubicaciones ub1 ON u1.Ubicacion = ub1.IdUbicacion
        LEFT JOIN Ubicaciones ub2 ON u2.Ubicacion = ub2.IdUbicacion
        ORDER BY rec.IdRelacion_Entre_Compras
    """, fetchall=True)
    
    # Obtener compras MADRE (solo productos tipo madre)
    compras_madre = execute_query("""
        SELECT ac.IdAsignadorCompra as id, 
               ac.NumeroSerie as numero_serie, 
               p.Nombre as nombre,
               u.IdUsuario as usuario_id,
               u.Nombre as usuario_nombre,
               p.Es_Producto_Madre as producto_es_madre,
               ub.IdUbicacion as ubicacion_id,
               ub.NombreEdificio as ubicacion_nombre
        FROM AsignadorCompra ac
        LEFT JOIN Productos p ON ac.Producto = p.IdProducto
        LEFT JOIN Usuarios u ON ac.Comprado_Para = u.IdUsuario
        LEFT JOIN Ubicaciones ub ON u.Ubicacion = ub.IdUbicacion
        WHERE ac.Comprado_Para IS NOT NULL
          AND p.Es_Producto_Madre = TRUE
        ORDER BY ac.Fecha_Compra DESC
    """, fetchall=True)
    
    # Obtener compras HIJO (solo productos tipo hijo)
    compras_hijo = execute_query("""
        SELECT ac.IdAsignadorCompra as id, 
               ac.NumeroSerie as numero_serie, 
               p.Nombre as nombre,
               u.IdUsuario as usuario_id,
               u.Nombre as usuario_nombre,
               p.Es_Producto_Madre as producto_es_madre,
               ub.IdUbicacion as ubicacion_id,
               ub.NombreEdificio as ubicacion_nombre
        FROM AsignadorCompra ac
        LEFT JOIN Productos p ON ac.Producto = p.IdProducto
        LEFT JOIN Usuarios u ON ac.Comprado_Para = u.IdUsuario
        LEFT JOIN Ubicaciones ub ON u.Ubicacion = ub.IdUbicacion
        WHERE ac.Comprado_Para IS NOT NULL
          AND p.Es_Producto_Madre = FALSE
        ORDER BY ac.Fecha_Compra DESC
    """, fetchall=True)
    
    # Obtener todas las ubicaciones disponibles
    ubicaciones_list = execute_query("""
        SELECT IdUbicacion as id, NombreEdificio as nombre 
        FROM Ubicaciones 
        ORDER BY NombreEdificio
    """, fetchall=True)
    
    return render_template('relaciones.html', 
                         relaciones=relaciones_list or [],
                         compras_madre=compras_madre or [],
                         compras_hijo=compras_hijo or [],
                         ubicaciones=ubicaciones_list or [])
@app.route('/relaciones/agregar', methods=['POST'])
def agregar_relacion():
    """Agregar nueva relación"""
    id_compra_madre = request.form.get('id_compra_madre')
    id_sub_compra = request.form.get('id_sub_compra')
    
    if not id_compra_madre or not id_sub_compra:
        flash('❌ Debe seleccionar ambas compras', 'error')
        return redirect(url_for('relaciones'))
    
    # Validar que no sea la misma compra
    if id_compra_madre == id_sub_compra:
        flash('❌ No puede vincular una compra consigo misma', 'error')
        return redirect(url_for('relaciones'))
    
    # Validar que las compras sean del mismo usuario
    compras_info = execute_query("""
        SELECT ac1.Comprado_Para as usuario_madre, 
               ac2.Comprado_Para as usuario_hija,
               p1.Es_Producto_Madre as producto_madre_es_madre,
               p2.Es_Producto_Madre as producto_hija_es_madre
        FROM AsignadorCompra ac1
        LEFT JOIN Productos p1 ON ac1.Producto = p1.IdProducto
        LEFT JOIN AsignadorCompra ac2 ON ac2.IdAsignadorCompra = %s
        LEFT JOIN Productos p2 ON ac2.Producto = p2.IdProducto
        WHERE ac1.IdAsignadorCompra = %s AND ac2.IdAsignadorCompra = %s
    """, (id_sub_compra, id_compra_madre, id_sub_compra), fetchone=True)
    
    if not compras_info:
        flash('❌ Una o ambas compras no existen', 'error')
        return redirect(url_for('relaciones'))
    
    usuario_madre = compras_info['usuario_madre']
    usuario_hija = compras_info['usuario_hija']
    
    # Validar que ambas compras tengan usuario asignado
    if not usuario_madre or not usuario_hija:
        flash('❌ Ambas compras deben tener un usuario asignado', 'error')
        return redirect(url_for('relaciones'))
    
    # Validar que sean del mismo usuario
    if usuario_madre != usuario_hija:
        flash('❌ Solo puede vincular compras del mismo usuario', 'error')
        return redirect(url_for('relaciones'))
    
    # Validar: Producto madre debe ser TRUE, producto hijo debe ser FALSE
    producto_madre_es_madre = compras_info['producto_madre_es_madre']
    producto_hija_es_madre = compras_info['producto_hija_es_madre']
    
    if not producto_madre_es_madre:
        flash('❌ La compra madre debe ser de un producto tipo "Madre" (ej: computadora)', 'error')
        return redirect(url_for('relaciones'))
    
    if producto_hija_es_madre:
        flash('❌ La sub compra debe ser de un producto tipo "Hijo/Componente" (ej: RAM, SSD)', 'error')
        return redirect(url_for('relaciones'))
    
    # Validar que la relación no exista ya
    relacion_existente = execute_query(
        "SELECT 1 FROM Relacion_Entre_Compras WHERE IdCompra_Madre = %s AND IdSub_Compra = %s",
        (id_compra_madre, id_sub_compra),
        fetchone=True
    )
    
    if relacion_existente:
        flash('❌ Esta relación ya existe', 'error')
        return redirect(url_for('relaciones'))
    
    # Insertar la relación
    execute_query(
        "INSERT INTO Relacion_Entre_Compras (IdCompra_Madre, IdSub_Compra) VALUES (%s, %s)",
        (id_compra_madre, id_sub_compra)
    )
    flash('✅ Relación agregada exitosamente', 'success')
    
    return redirect(url_for('relaciones'))

@app.route('/relaciones/eliminar/<int:id>')
def eliminar_relacion(id):
    """Eliminar relación"""
    execute_query("DELETE FROM Relacion_Entre_Compras WHERE IdRelacion_Entre_Compras = %s", (id,))
    flash('✅ Relación eliminada exitosamente', 'success')
    return redirect(url_for('relaciones'))

# ========== INICIO DE LA APLICACIÓN ==========
if __name__ == '__main__':
    print("=" * 60)
    print("🐳 Sistema de Inventario - Dockerizado")
    print("=" * 60)
    print(f"📦 PostgreSQL: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    print(f"🌐 Aplicación: http://0.0.0.0:5000")
    print("=" * 60)
    
    # Verificar conexión inicial
    print("🔍 Probando conexión a la base de datos...")
    if execute_query("SELECT 1 as test", fetchone=True):
        print("✅ Conexión exitosa a PostgreSQL")
    else:
        print("⚠️  No se pudo conectar a PostgreSQL")
    
    app.run(host='0.0.0.0', port=5000, debug=True)