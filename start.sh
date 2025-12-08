#!/bin/bash

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐳 SISTEMA DE INVENTARIO DOCKERIZADO${NC}"
echo "=========================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi

# Verificar puerto 5432
if lsof -i :5432 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Puerto 5432 está en uso${NC}"
    echo "Usando puerto 5433 para PostgreSQL..."
fi

# Limpiar
echo -e "${YELLOW}🧹 Limpiando contenedores anteriores...${NC}"
docker compose down -v 2>/dev/null || true

# Construir e iniciar
echo -e "${BLUE}🚀 Construyendo e iniciando servicios...${NC}"
docker compose up --build -d

echo -e "${YELLOW}⏳ Esperando a que los servicios estén listos...${NC}"
sleep 15

# Verificar estado
echo ""
echo -e "${BLUE}📊 ESTADO DE LOS SERVICIOS:${NC}"
echo "================================"
docker compose ps

# Preguntar por seed
echo ""
echo -e "${YELLOW}🌱 ¿Desea cargar datos de prueba? (s/n)${NC}"
read -p "> " respuesta

if [[ $respuesta == "s" || $respuesta == "S" ]]; then
    echo -e "${BLUE}📦 Ejecutando seed de datos...${NC}"
    docker compose run --rm seed
fi

echo ""
echo -e "${GREEN}✅ ¡SISTEMA LISTO!${NC}"
echo "===================="
echo -e "${BLUE}🌐 Aplicación:${NC} http://localhost:5000"
echo -e "${BLUE}🐘 PostgreSQL:${NC} localhost:5433 (5432 dentro de Docker)"
echo -e "${BLUE}👤 Usuario BD:${NC} admin"
echo -e "${BLUE}🔑 Contraseña BD:${NC} admin123"
echo ""
echo -e "${YELLOW}📝 COMANDOS ÚTILES:${NC}"
echo "  Ver logs: docker compose logs -f"
echo "  Detener: docker compose down"
echo "  Reiniciar: docker compose restart"
echo "  Ejecutar seed: docker compose run --rm seed"
echo "  Acceder a BD: docker exec -it inventario_db psql -U admin -d sistema_inventario"
echo ""