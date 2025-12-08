#!/bin/bash

echo "🌱 Ejecutando seed de datos..."
docker compose run --rm seed
echo "✅ Seed completado"