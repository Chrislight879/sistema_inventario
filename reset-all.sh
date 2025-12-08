#!/bin/bash

echo "🔄 REINICIANDO SISTEMA COMPLETO"
echo "================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Detener y eliminar todo
echo -e "${YELLOW}1. Deteniendo contenedores...${NC}"
docker compose down -v

# 2. Limpiar Docker
echo -e "${YELLOW}2. Limpiando Docker...${NC}"
docker system prune -f

# 3. Construir
echo -e "${BLUE}3. Construyendo imágenes...${NC}"
docker compose build

# 4. Iniciar
echo -e "${BLUE}4. Iniciando servicios...${NC}"
docker compose up -d

# 5. Esperar
echo -e "${YELLOW}5. Esperando a que los servicios estén listos...${NC}"
sleep 20

# 6. Verificar
echo -e "${BLUE}6. Verificando servicios...${NC}"
docker compose ps

# 7. Ejecutar seed
echo -e "${GREEN}7. Ejecutando seed de datos...${NC}"
docker compose run --rm seed

echo ""
echo -e "${GREEN}✅ ¡SISTEMA REINICIADO COMPLETAMENTE!${NC}"
echo ""
echo -e "${BLUE}🌐 Aplicación:${NC} http://localhost:5000"
echo -e "${BLUE}🐘 PostgreSQL:${NC} localhost:5433"
echo -e "${BLUE}👤 Usuario BD:${NC} admin"
echo -e "${BLUE}🔑 Contraseña BD:${NC} admin123"