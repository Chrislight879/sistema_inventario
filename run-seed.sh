#!/bin/bash

echo "🌱 Ejecutando seed para poblar datos de prueba..."
echo "=================================================="

echo "🔍 Verificando que PostgreSQL esté funcionando..."
docker compose exec postgres pg_isready -U admin

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL está listo"
    
    echo ""
    echo "📦 Ejecutando seed..."
    docker compose exec web python seed-db-docker.py
    
    echo ""
    echo "✅ Seed completado!"
    echo "🌐 Accede a: http://localhost:5000"
else
    echo "❌ PostgreSQL no está disponible"
    echo "Primero ejecuta: docker compose up -d"
    exit 1
fi