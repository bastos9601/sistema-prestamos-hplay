#!/usr/bin/env bash
# Script de build personalizado para Render

echo "🚀 Iniciando build en Render..."

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias básicas primero
echo "📦 Instalando dependencias básicas..."
pip install -r requirements-minimal.txt

# Verificar que las básicas funcionen
echo "✅ Verificando dependencias básicas..."
python -c "import flask, psycopg2; print('Dependencias básicas instaladas correctamente')"

# Ahora instalar dependencias adicionales
echo "📦 Instalando dependencias adicionales..."
pip install reportlab==3.6.12 Pillow==9.5.0 qrcode==7.4.2 requests==2.28.2

# Verificar instalación completa
echo "✅ Verificando instalación completa..."
python -c "import flask, psycopg2, reportlab, PIL, qrcode, requests; print('Todas las dependencias instaladas correctamente')"

echo "🎉 Build completado exitosamente!"
