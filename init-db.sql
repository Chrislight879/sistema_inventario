-- Sistema de Inventario - Estructura inicial

CREATE TABLE IF NOT EXISTS Categorias (
    IdCategoria SERIAL PRIMARY KEY,
    Nombre_Categoria VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Productos (
    IdProducto SERIAL PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    Categoria BIGINT NOT NULL,
    Es_Producto_Madre BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (Categoria) REFERENCES Categorias(IdCategoria)
);

CREATE TABLE IF NOT EXISTS Proveedores (
    IdProveedor SERIAL PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Ubicaciones (
    IdUbicacion SERIAL PRIMARY KEY,
    NombreEdificio VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Usuarios (
    IdUsuario SERIAL PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    Ubicacion BIGINT NOT NULL,
    Ubicacion_Especifica VARCHAR(255),
    FOREIGN KEY (Ubicacion) REFERENCES Ubicaciones(IdUbicacion)
);

CREATE TABLE IF NOT EXISTS AsignadorCompra (
    IdAsignadorCompra SERIAL PRIMARY KEY,
    Fecha_Compra DATE NOT NULL,
    Producto BIGINT NOT NULL,
    Proveedor BIGINT NOT NULL,
    Fin_Garantia DATE,
    Comprado_Para BIGINT,
    NumeroSerie VARCHAR(255),
    FOREIGN KEY (Producto) REFERENCES Productos(IdProducto),
    FOREIGN KEY (Proveedor) REFERENCES Proveedores(IdProveedor),
    FOREIGN KEY (Comprado_Para) REFERENCES Usuarios(IdUsuario)
);

CREATE TABLE IF NOT EXISTS Relacion_Entre_Compras (
    IdRelacion_Entre_Compras SERIAL PRIMARY KEY,
    IdCompra_Madre BIGINT NOT NULL,
    IdSub_Compra BIGINT NOT NULL,
    FOREIGN KEY (IdCompra_Madre) REFERENCES AsignadorCompra(IdAsignadorCompra),
    FOREIGN KEY (IdSub_Compra) REFERENCES AsignadorCompra(IdAsignadorCompra)
);

CREATE TABLE IF NOT EXISTS Mantenimientos (
    IdMantenimiento SERIAL PRIMARY KEY,
    Compra BIGINT NOT NULL,
    Problema_Presentado VARCHAR(500),
    Fecha_Inicio DATE,
    Observaciones VARCHAR(500),
    Diagnostico VARCHAR(500),
    Fecha_Final DATE,
    FOREIGN KEY (Compra) REFERENCES AsignadorCompra(IdAsignadorCompra)
);

-- Datos mínimos iniciales
INSERT INTO Categorias (Nombre_Categoria) VALUES 
('General') ON CONFLICT (Nombre_Categoria) DO NOTHING;

INSERT INTO Proveedores (Nombre) VALUES 
('Proveedor General') ON CONFLICT (Nombre) DO NOTHING;

INSERT INTO Ubicaciones (NombreEdificio) VALUES 
('Edificio Principal') ON CONFLICT (NombreEdificio) DO NOTHING;

-- Índices
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON Productos(Categoria);
CREATE INDEX IF NOT EXISTS idx_usuarios_ubicacion ON Usuarios(Ubicacion);
CREATE INDEX IF NOT EXISTS idx_compras_producto ON AsignadorCompra(Producto);
CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON AsignadorCompra(Proveedor);
CREATE INDEX IF NOT EXISTS idx_mantenimientos_compra ON Mantenimientos(Compra);
CREATE INDEX IF NOT EXISTS idx_productos_es_madre ON Productos(Es_Producto_Madre);