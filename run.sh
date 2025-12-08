#!/bin/bash

echo "🐳 Iniciando Sistema de Inventario Dockerizado..."
echo "=" * 60

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Verificar si docker-compose está instalado
if ! docker compose version &> /dev/null; then
    echo "❌ docker-compose no está instalado"
    exit 1
fi

# Limpiar contenedores previos (opcional)
echo "🧹 Limpiando contenedores previos..."
docker compose down 2>/dev/null

# Construir e iniciar
echo "🚀 Construyendo e iniciando contenedores..."
docker compose up --build -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

# Preguntar si se desea ejecutar seed
echo ""
echo "📊 ¿Desea poblar la base de datos con datos de prueba?"
echo "   y = Sí, ejecutar seed con datos de prueba"
echo "   n = No, mantener base de datos vacía"
read -p "   Su elección [y/N]: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🌱 Ejecutando seed para poblar datos de prueba..."
    docker run --rm \
        --network inventario_default \
        -e DB_HOST=postgres \
        -e DB_PORT=5432 \
        -e DB_NAME=sistema_inventario \
        -e DB_USER=admin \
        -e DB_PASSWORD=admin123 \
        -v $(pwd)/seed-db-docker.py:/app/seed-db-docker.py \
        -v $(pwd)/requirements.txt:/app/requirements.txt \
        python:3.11-slim \
        sh -c "pip install -r /app/requirements.txt && python /app/seed-db-docker.py"
else
    echo "⚠️  Base de datos se mantendrá con estructura básica"
fi

echo ""
echo "📊 Estado de los contenedores:"
docker compose ps

echo ""
echo "✅ Sistema listo!"
echo "🌐 Aplicación: http://localhost:5000"
echo "📊 PostgreSQL: localhost:5433 (5432 dentro de Docker)"
echo "👤 Usuario BD: admin"
echo "🔑 Contraseña BD: admin123"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs: docker compose logs -f"
echo "   Detener: docker compose down"
echo "   Reiniciar: docker compose restart"
echo "   Ejecutar seed: docker compose run --rm seed"
echo "   Acceder a BD: docker exec -it inventario_db psql -U admin -d sistema_inventario"
echo ""