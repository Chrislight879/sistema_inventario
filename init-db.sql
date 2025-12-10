-- Sistema de Inventario - Estructura inicial

-- Eliminar tablas si existen (en orden correcto por dependencias)
DROP TABLE IF EXISTS Mantenimientos CASCADE;
DROP TABLE IF EXISTS AsignadorCompra CASCADE;
DROP TABLE IF EXISTS Usuarios CASCADE;
DROP TABLE IF EXISTS Ubicaciones CASCADE;
DROP TABLE IF EXISTS Proveedores CASCADE;
DROP TABLE IF EXISTS Productos CASCADE;
DROP TABLE IF EXISTS Categorias CASCADE;

-- ==================================================
-- TABLAS PRINCIPALES
-- ==================================================

-- Tabla de categorías
CREATE TABLE Categorias (
    IdCategoria SERIAL PRIMARY KEY,
    Nombre_Categoria VARCHAR(255) NOT NULL UNIQUE
);

-- Tabla de productos
CREATE TABLE Productos (
    IdProducto SERIAL PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    Precio_Estandar DECIMAL(10,2),
    Categoria BIGINT NOT NULL,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (Categoria) 
        REFERENCES Categorias(IdCategoria) ON DELETE RESTRICT
);

-- Tabla de proveedores
CREATE TABLE Proveedores (
    IdProveedor SERIAL PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL UNIQUE,
    Contacto VARCHAR(255)
);

-- Tabla de ubicaciones
CREATE TABLE Ubicaciones (
    IdUbicacion SERIAL PRIMARY KEY,
    NombreEdificio VARCHAR(255) NOT NULL UNIQUE
);

-- Tabla de usuarios
CREATE TABLE Usuarios (
    IdUsuario SERIAL PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    Ubicacion BIGINT NOT NULL,
    Ubicacion_Especifica VARCHAR(255),
    CONSTRAINT fk_usuario_ubicacion FOREIGN KEY (Ubicacion) 
        REFERENCES Ubicaciones(IdUbicacion) ON DELETE RESTRICT
);

-- Tabla de compras
CREATE TABLE AsignadorCompra (
    IdAsignadorCompra SERIAL PRIMARY KEY,
    Fecha_Compra DATE NOT NULL DEFAULT CURRENT_DATE,
    Producto BIGINT,
    Precio DECIMAL(10,2),
    Proveedor BIGINT NOT NULL,
    Fin_Garantia DATE,
    Comprado_Para BIGINT,
    NumeroSerie VARCHAR(255),
    CONSTRAINT fk_compra_producto FOREIGN KEY (Producto) 
        REFERENCES Productos(IdProducto) ON DELETE RESTRICT,
    CONSTRAINT fk_compra_proveedor FOREIGN KEY (Proveedor) 
        REFERENCES Proveedores(IdProveedor) ON DELETE RESTRICT,
    CONSTRAINT fk_compra_usuario FOREIGN KEY (Comprado_Para) 
        REFERENCES Usuarios(IdUsuario) ON DELETE SET NULL
);

-- Tabla de mantenimientos
CREATE TABLE Mantenimientos (
    IdMantenimiento SERIAL PRIMARY KEY,
    Compra BIGINT NOT NULL,
    Problema_Presentado TEXT,
    Fecha_Inicio DATE DEFAULT CURRENT_DATE,
    Observaciones TEXT,
    Diagnostico TEXT,
    Fecha_Final DATE,
    CONSTRAINT fk_mantenimiento_compra FOREIGN KEY (Compra) 
        REFERENCES AsignadorCompra(IdAsignadorCompra) ON DELETE CASCADE
);

-- ==================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ==================================================

CREATE INDEX idx_productos_categoria ON Productos(Categoria);
CREATE INDEX idx_productos_nombre ON Productos(Nombre);

CREATE INDEX idx_usuarios_ubicacion ON Usuarios(Ubicacion);
CREATE INDEX idx_usuarios_nombre ON Usuarios(Nombre);

CREATE INDEX idx_compras_producto ON AsignadorCompra(Producto);
CREATE INDEX idx_compras_proveedor ON AsignadorCompra(Proveedor);
CREATE INDEX idx_compras_usuario ON AsignadorCompra(Comprado_Para);
CREATE INDEX idx_compras_fecha ON AsignadorCompra(Fecha_Compra);

CREATE INDEX idx_mantenimientos_compra ON Mantenimientos(Compra);
CREATE INDEX idx_mantenimientos_fecha_inicio ON Mantenimientos(Fecha_Inicio);

-- ==================================================
-- DATOS INICIALES
-- ==================================================

-- Categorías básicas
INSERT INTO Categorias (Nombre_Categoria) VALUES 
    ('Consumible'),
    ('Equipo electrónico'),
    ('Componente electrónico'),
    ('Servicios');

-- Proveedores
INSERT INTO Proveedores (Nombre, Contacto) VALUES 
    ('GALERIA S.A. DE C.V.', 'tel: +503 2564-6840'),
    ('FAST SYSTEM COMPUTER S.A. DE C.V.', 'tel: +503 2226-8150'),
    ('COPIADORAS DE EL SALVADOR, S.A. DE C.V.', 'tel: +503 2260-6444'),
    ('COMPANIA SALVADORENA DE SEGURIDAD, S.A. DE C.V.', 'tel: +503 2500-5222'),
    ('INNOVATION BUSINESS SUSTAINABILITY, S.A. DE C.V.', 'tel: +503 2262-6730'),
    ('JAKO SOLUTIONS S.A. DE C.V.','tel: +503 2288-2443'),
    ('ANYDESK SOFTWARE GMBH', 'e-mail: info@anydesk.com'),
    ('ACOSA, S.A. DE C.V.', 'tel: +503 2510-2393'),
    ('TECNOLOGIA Y SUMINISTROS, S.A. DE C.V.', 'tel: +503 2264-6966'),
    ('STB COMPUTER,S.A. DE C.V.', 'e-mail: garantias01@stbgroup.com.sv');

-- Ubicaciones
INSERT INTO Ubicaciones (NombreEdificio) VALUES 
    ('OFICINA CENTRAL SAN SALVADOR'),
    ('SUCURSAL VEINTINUEVE SAN SALVADOR'),
    ('SUCURSAL VENEZUELA SAN SALVADOR'),
    ('SUCURSAL SAN MIGUEL'),
    ('SUCURSAL SANTA ANA'),
    ('SUCURSAL SONSONATE'),
    ('SUNMOTORS  ZACATECOLUCA'),
    ('SUNMOTORS  USULUTAN'),
    ('MULTIBALEROS SAN SALVADOR'),
    ('RODACENTRO'),
    ('AGENTE EXTERNO');


INSERT INTO Productos (Nombre, Categoria) VALUES 
    --=============2024============
    --CONSUMIBLES
    ('TONER HP 30X BLACK -CF230A', 1),
    ('TONER HP 145X BLACK -W1450X', 1),
    ('TAMBOR NEGRO 32A -CF232A', 1),
    ('TECLADO USB LOGITECH K 120 SP -KEYLOGITECHSP', 1),
    ('MOUSE USB LOGITECH M110 -MOULGUSB/PS2', 1),
    ('UNIDAD DE IMAGEN M2040 -DK11502RV93010', 1),
    ('KEY/MOU LOGITECH COMBO TEC/MOU USB LOGITECH MK200', 1),
    ('LOGITECH MOUSE M110 SILENT CABLEADO', 1),
    
    --2 = EQUIPO ELECTRONICO, 3 = COMPONENTE ELECTRONICO, 4 = SERVICIOS
    ('SERVICIO POR ALARMA DE SEGURIDAD', 4),
    ('SERVICIO DE ANTIVIRUS ESET PROTECT ENTRY CLOUD', 4),
    ('SERVICIO DE ALQUILER DE EQUIPO PARA TOMA DE INVENTARIO', 4),
    ('SWITCH DAHUA 24 P -DHPFS302424GT', 2),
    ('UPS APC 700 -BVX700LULM', 2),
    ('LAPTOP DELL LATITUDE 3550 NOTEBOOK 15.6', 2),
    ('TARJETA RED D LINK DWA 132 WIRELESS USB NANO', 2),
    ('CLON I 5 8 GB 500 SSD', 2),
    ('FUENTE DE PODER IMEXX ATX 600 WATTS 24 PIN SATA', 3),
    ('DIMM DDR4 16GB KINGSTON KVR32N', 3),
    ('PLACA SENCILLA METAL MONTAJE SSD 2.5 KINGSTON', 3),
    ('APC BACK UPS CA 120 V', 2),
    ('APC BACK UPS PRO BX1000M LM60 CA 120 V', 2),
    ('KINGSTON SSD 960 GB A400 SATA 3 2.5 SSD', 3),
    ('CLON I 7 16 GB 960 SSD', 2),
    ('HP LASERJET MULTIFUNCION', 2),
    ('MONITOR 19.5 AOC', 2),
    ('MONITOR 19.5 AOC', 2),
    ('MONITOR 19.5 AOC', 2),

    -- PERIFÉRICOS
    ('Mouse Logitech M185 Inalámbrico', 3),
    ('Mouse Logitech MX Master 3', 3),
    ('Teclado Logitech K120', 3),
    ('Teclado Mecánico Corsair K95', 3),
    ('Monitor Dell 24" Full HD P2422H', 3),
    ('Monitor LG 27" 4K UltraFine', 3),
    ('Webcam Logitech C920 HD Pro', 3),
    ('Impresora HP LaserJet Pro M404dn', 3),
    ('Impresora Multifuncional Epson EcoTank L3250', 3),
    ('Scanner Canon CanoScan LiDE 400', 3),
    
    -- SOFTWARE
    ('Licencia Microsoft Office 365 Business', 6),
    ('Licencia Windows 11 Pro', 6),
    ('Licencia Adobe Creative Cloud', 6),
    ('Licencia Antivirus Kaspersky', 6);

-- Usuarios de ejemplo
INSERT INTO Usuarios (Nombre, Ubicacion, Ubicacion_Especifica) VALUES 
    ('Juan Pérez García', 5, 'Oficina 101'),
    ('María González López', 6, 'Oficina 205'),
    ('Carlos Rodríguez Sánchez', 5, 'Cubículo 15'),
    ('Ana Martínez Torres', 7, 'Oficina 310'),
    ('Luis Torres Ramírez', 1, 'Sala de Juntas Principal'),
    ('Patricia Hernández Cruz', 6, 'Oficina 208'),
    ('Roberto Jiménez Flores', 4, 'Laboratorio A'),
    ('Carmen Díaz Morales', 2, 'Dirección Administrativa'),
    ('Francisco Ruiz Castro', 8, 'Sala Servidores - Rack 3'),
    ('Elena Vargas Ortiz', 7, 'Oficina 305');

-- COMPRAS
INSERT INTO AsignadorCompra (Fecha_Compra, Producto, Proveedor, Fin_Garantia, Comprado_Para, NumeroSerie) VALUES 
    ('2024-01-15', 1, 2, '2027-01-15', 1, 'DELL-OPT-7090-001'),
    ('2024-01-20', 2, 3, '2027-01-20', 2, 'HP-ELITE-800-002'),
    ('2024-02-10', 3, 4, '2027-02-10', 3, 'LENOVO-T14-003'),
    ('2024-02-15', 4, 3, '2027-02-15', 4, 'HP-PB450-004'),
    ('2024-03-01', 1, 2, '2027-03-01', 5, 'DELL-OPT-7090-005'),
    ('2024-03-05', 6, 3, '2027-03-05', 6, 'HP-Z4-006'),
    ('2024-03-20', 3, 4, '2027-03-20', 7, 'LENOVO-T14-007'),
    ('2024-04-01', 5, 2, '2029-04-01', 9, 'DELL-R740-008'),
    ('2024-04-10', 7, 7, '2027-04-10', NULL, 'CISCO-2960-009'),
    ('2024-04-15', 8, 6, '2026-04-15', NULL, 'TP-LINK-AX6000-010');

INSERT INTO AsignadorCompra (Fecha_Compra, Producto, Proveedor, Fin_Garantia, Comprado_Para, NumeroSerie) VALUES 
    ('2024-01-16', 9, 5, '2027-01-16', 1, 'RAM-8GB-K-001'),
    ('2024-01-21', 12, 5, '2027-01-21', 2, 'SSD-500-S-002'),
    ('2024-02-11', 10, 5, '2027-02-11', 3, 'RAM-16GB-C-003'),
    ('2024-02-16', 13, 5, '2027-02-16', 4, 'SSD-1TB-W-004'),
    ('2024-03-02', 11, 5, '2027-03-02', 5, 'RAM-32GB-C-005'),
    ('2024-03-06', 17, 5, '2027-03-06', 6, 'GPU-1650-006'),
    ('2024-03-21', 14, 5, '2027-03-21', 7, 'HDD-1TB-S-007'),
    ('2024-04-02', 15, 5, '2029-04-02', 9, 'HDD-2TB-W-008');

INSERT INTO AsignadorCompra (Fecha_Compra, Producto, Proveedor, Fin_Garantia, Comprado_Para, NumeroSerie) VALUES 
    ('2024-01-17', 23, 5, '2027-01-17', 1, 'MON-DELL24-001'),
    ('2024-01-22', 19, 5, '2027-01-22', 2, 'MOUSE-M185-002'),
    ('2024-02-12', 21, 5, '2027-02-12', 3, 'KB-K120-003'),
    ('2024-02-17', 24, 5, '2027-02-17', 4, 'MON-LG27-004');

-- MANTENIMIENTOS de ejemplo
INSERT INTO Mantenimientos (Compra, Problema_Presentado, Fecha_Inicio, Observaciones, Diagnostico, Fecha_Final) VALUES 
    (1, 'Equipo no enciende correctamente', '2024-06-01', 'Se revisó fuente de alimentación', 'Fuente de poder con falla, se reemplazó componente', '2024-06-03'),
    (2, 'Pantalla azul frecuente (BSOD)', '2024-06-10', 'Se ejecutaron diagnósticos de memoria RAM', 'Módulo de RAM defectuoso detectado, en proceso de garantía', '2024-06-15'),
    (3, 'Sistema operativo muy lento', '2024-06-20', 'Se realizó limpieza de archivos y desfragmentación', 'Disco fragmentado y malware detectado, sistema limpiado', '2024-06-21'),
    (5, 'Ventilador hace ruido excesivo', '2024-07-05', 'Inspección de ventiladores internos', 'Ventilador del CPU con rodamiento dañado, reemplazado', '2024-07-06'),
    (8, 'Servidor no responde a peticiones', '2024-07-15', 'Revisión de configuración de red y servicios', 'Servicio de red detenido, se reinició y configuró correctamente', '2024-07-15');

-- ==================================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- ==================================================

COMMENT ON TABLE Productos IS 'Catálogo de productos';
COMMENT ON TABLE AsignadorCompra IS 'Registro de todas las compras realizadas. Puede tener o no un usuario asignado';
COMMENT ON TABLE Mantenimientos IS 'Historial de mantenimientos realizados a las compras';
COMMENT ON COLUMN AsignadorCompra.Comprado_Para IS 'Usuario al que se asigna la compra. NULL si no está asignado a nadie específico';

-- ==================================================
-- VERIFICACIÓN FINAL
-- ==================================================

DO $$
BEGIN
    RAISE NOTICE '================================================';
    RAISE NOTICE 'BASE DE DATOS INICIALIZADA CORRECTAMENTE';
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Categorías: %', (SELECT COUNT(*) FROM Categorias);
    RAISE NOTICE 'Productos: %', (SELECT COUNT(*) FROM Productos);
    RAISE NOTICE 'Proveedores: %', (SELECT COUNT(*) FROM Proveedores);
    RAISE NOTICE 'Ubicaciones: %', (SELECT COUNT(*) FROM Ubicaciones);
    RAISE NOTICE 'Usuarios: %', (SELECT COUNT(*) FROM Usuarios);
    RAISE NOTICE 'Compras: %', (SELECT COUNT(*) FROM AsignadorCompra);
    RAISE NOTICE 'Mantenimientos: %', (SELECT COUNT(*) FROM Mantenimientos);
    RAISE NOTICE '================================================';
END $$;