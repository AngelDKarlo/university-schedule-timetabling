#!/bin/bash

# Script para iniciar el servidor web del Sistema de Horarios ITI
# Universidad Politécnica de Victoria

echo "======================================"
echo "🎓 SISTEMA DE HORARIOS ITI - WEB"
echo "Universidad Politécnica de Victoria"
echo "======================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Verificar si el puerto 5000 está ocupado
PORT=5000
if lsof -i :$PORT >/dev/null 2>&1; then
    echo ""
    echo "⚠️  Puerto $PORT está ocupado"
    PID=$(lsof -t -i:$PORT)
    echo "   Proceso: $(ps -p $PID -o comm= 2>/dev/null || echo 'desconocido') (PID: $PID)"
    echo ""
    read -p "¿Deseas cerrar el proceso y continuar? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "🔨 Cerrando proceso $PID..."
        kill -9 $PID 2>/dev/null
        sleep 1
        if lsof -i:$PORT >/dev/null 2>&1; then
            echo "❌ No se pudo cerrar. Intenta manualmente: sudo kill -9 $PID"
            exit 1
        fi
        echo "✓ Puerto liberado"
    else
        echo "❌ Operación cancelada"
        exit 1
    fi
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear entorno virtual"
        exit 1
    fi
    
    echo "✓ Entorno virtual creado"
fi

# Activar entorno virtual
echo ""
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar/actualizar dependencias
echo ""
echo "📥 Instalando dependencias..."
pip install -q --upgrade pip
pip install -q -r web/requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error al instalar dependencias"
    exit 1
fi

echo "✓ Dependencias instaladas"

# Crear directorios necesarios
mkdir -p web/uploads
mkdir -p web/exports

echo ""
echo "======================================"
echo "🚀 Iniciando servidor web..."
echo "======================================"
echo ""
echo "📍 URL: http://localhost:5000"
echo "📍 URL Red Local: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Iniciar servidor
cd web/backend
python3 app.py
