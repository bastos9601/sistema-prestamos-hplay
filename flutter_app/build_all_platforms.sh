#!/bin/bash

# 🚀 Script de Build Multiplataforma - Sistema de Préstamos
# Este script construye la aplicación Flutter para todas las plataformas

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Función para verificar si Flutter está instalado
check_flutter() {
    if ! command -v flutter &> /dev/null; then
        print_error "Flutter no está instalado o no está en el PATH"
        print_status "Por favor, instala Flutter siguiendo la guía en install_flutter.md"
        exit 1
    fi
    
    print_success "Flutter encontrado: $(flutter --version | head -n 1)"
}

# Función para limpiar builds anteriores
clean_builds() {
    print_status "Limpiando builds anteriores..."
    flutter clean
    flutter pub get
    print_success "Limpieza completada"
}

# Función para verificar dependencias
check_dependencies() {
    print_status "Verificando dependencias..."
    flutter doctor
    print_success "Verificación de dependencias completada"
}

# Función para construir APK de Android
build_android() {
    print_header "Construyendo para Android"
    
    print_status "Construyendo APK de debug..."
    flutter build apk --debug
    print_success "APK de debug construido en build/app/outputs/flutter-apk/app-debug.apk"
    
    print_status "Construyendo APK de release..."
    flutter build apk --release
    print_success "APK de release construido en build/app/outputs/flutter-apk/app-release.apk"
    
    print_status "Construyendo APK dividido por arquitectura..."
    flutter build apk --split-per-abi
    print_success "APKs divididos construidos en build/app/outputs/flutter-apk/"
    
    print_status "Construyendo App Bundle para Google Play..."
    flutter build appbundle
    print_success "App Bundle construido en build/app/outputs/bundle/release/app-release.aab"
}

# Función para construir para iOS
build_ios() {
    print_header "Construyendo para iOS"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "Construyendo para iOS..."
        flutter build ios --release
        print_success "Build de iOS completado"
        
        print_status "Construyendo IPA..."
        flutter build ipa
        print_success "IPA construido en build/ios/ipa/"
    else
        print_warning "iOS solo se puede construir en macOS"
    fi
}

# Función para construir para Web
build_web() {
    print_header "Construyendo para Web"
    
    print_status "Construyendo para Web..."
    flutter build web --release
    print_success "Build de Web completado en build/web/"
    
    # Crear archivo de información
    echo "Build completado: $(date)" > build/web/build_info.txt
    echo "Flutter version: $(flutter --version | head -n 1)" >> build/web/build_info.txt
}

# Función para construir para Windows
build_windows() {
    print_header "Construyendo para Windows"
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        print_status "Construyendo para Windows..."
        flutter build windows --release
        print_success "Build de Windows completado en build/windows/runner/Release/"
    else
        print_warning "Windows solo se puede construir en Windows o WSL"
    fi
}

# Función para construir para macOS
build_macos() {
    print_header "Construyendo para macOS"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "Construyendo para macOS..."
        flutter build macos --release
        print_success "Build de macOS completado en build/macos/Build/Products/Release/"
    else
        print_warning "macOS solo se puede construir en macOS"
    fi
}

# Función para construir para Linux
build_linux() {
    print_header "Construyendo para Linux"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Construyendo para Linux..."
        flutter build linux --release
        print_success "Build de Linux completado en build/linux/x64/release/bundle/"
    else
        print_warning "Linux solo se puede construir en Linux"
    fi
}

# Función para crear resumen de builds
create_build_summary() {
    print_header "Resumen de Builds"
    
    echo "📱 **APK Android**" > BUILD_SUMMARY.md
    echo "- Debug: build/app/outputs/flutter-apk/app-debug.apk" >> BUILD_SUMMARY.md
    echo "- Release: build/app/outputs/flutter-apk/app-release.apk" >> BUILD_SUMMARY.md
    echo "- App Bundle: build/app/outputs/bundle/release/app-release.aab" >> BUILD_SUMMARY.md
    echo "" >> BUILD_SUMMARY.md
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 **iOS**" >> BUILD_SUMMARY.md
        echo "- Build: build/ios/" >> BUILD_SUMMARY.md
        echo "- IPA: build/ios/ipa/" >> BUILD_SUMMARY.md
        echo "" >> BUILD_SUMMARY.md
        
        echo "💻 **macOS**" >> BUILD_SUMMARY.md
        echo "- Build: build/macos/Build/Products/Release/" >> BUILD_SUMMARY.md
        echo "" >> BUILD_SUMMARY.md
    fi
    
    echo "🌐 **Web**" >> BUILD_SUMMARY.md
    echo "- Build: build/web/" >> BUILD_SUMMARY.md
    echo "" >> BUILD_SUMMARY.md
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "🪟 **Windows**" >> BUILD_SUMMARY.md
        echo "- Build: build/windows/runner/Release/" >> BUILD_SUMMARY.md
        echo "" >> BUILD_SUMMARY.md
    fi
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "🐧 **Linux**" >> BUILD_SUMMARY.md
        echo "- Build: build/linux/x64/release/bundle/" >> BUILD_SUMMARY.md
        echo "" >> BUILD_SUMMARY.md
    fi
    
    echo "📊 **Información del Build**" >> BUILD_SUMMARY.md
    echo "- Fecha: $(date)" >> BUILD_SUMMARY.md
    echo "- Flutter: $(flutter --version | head -n 1)" >> BUILD_SUMMARY.md
    echo "- Sistema: $OSTYPE" >> BUILD_SUMMARY.md
    
    print_success "Resumen de builds creado en BUILD_SUMMARY.md"
}

# Función para mostrar uso
show_usage() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  -a, --android     Construir solo para Android"
    echo "  -i, --ios         Construir solo para iOS (macOS)"
    echo "  -w, --web         Construir solo para Web"
    echo "  -d, --windows     Construir solo para Windows"
    echo "  -m, --macos       Construir solo para macOS"
    echo "  -l, --linux       Construir solo para Linux"
    echo "  -c, --clean       Limpiar builds anteriores"
    echo "  -h, --help        Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0                 # Construir para todas las plataformas"
    echo "  $0 -a             # Solo Android"
    echo "  $0 -w -d          # Solo Web y Windows"
    echo "  $0 -c             # Solo limpiar"
}

# Función principal
main() {
    print_header "Sistema de Préstamos - Build Multiplataforma"
    
    # Verificar Flutter
    check_flutter
    
    # Variables para controlar qué construir
    BUILD_ANDROID=false
    BUILD_IOS=false
    BUILD_WEB=false
    BUILD_WINDOWS=false
    BUILD_MACOS=false
    BUILD_LINUX=false
    CLEAN_ONLY=false
    
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--android)
                BUILD_ANDROID=true
                shift
                ;;
            -i|--ios)
                BUILD_IOS=true
                shift
                ;;
            -w|--web)
                BUILD_WEB=true
                shift
                ;;
            -d|--windows)
                BUILD_WINDOWS=true
                shift
                ;;
            -m|--macos)
                BUILD_MACOS=true
                shift
                ;;
            -l|--linux)
                BUILD_LINUX=true
                shift
                ;;
            -c|--clean)
                CLEAN_ONLY=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Opción desconocida: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Si no se especificó ninguna plataforma, construir para todas
    if [[ "$BUILD_ANDROID" == false && "$BUILD_IOS" == false && "$BUILD_WEB" == false && "$BUILD_WINDOWS" == false && "$BUILD_MACOS" == false && "$BUILD_LINUX" == false ]]; then
        BUILD_ANDROID=true
        BUILD_IOS=true
        BUILD_WEB=true
        BUILD_WINDOWS=true
        BUILD_MACOS=true
        BUILD_LINUX=true
    fi
    
    # Limpiar si se solicita
    if [[ "$CLEAN_ONLY" == true ]]; then
        clean_builds
        exit 0
    fi
    
    # Limpiar antes de construir
    clean_builds
    
    # Verificar dependencias
    check_dependencies
    
    # Construir según las opciones seleccionadas
    if [[ "$BUILD_ANDROID" == true ]]; then
        build_android
    fi
    
    if [[ "$BUILD_IOS" == true ]]; then
        build_ios
    fi
    
    if [[ "$BUILD_WEB" == true ]]; then
        build_web
    fi
    
    if [[ "$BUILD_WINDOWS" == true ]]; then
        build_windows
    fi
    
    if [[ "$BUILD_MACOS" == true ]]; then
        build_macos
    fi
    
    if [[ "$BUILD_LINUX" == true ]]; then
        build_linux
    fi
    
    # Crear resumen
    create_build_summary
    
    print_header "¡Build Completado Exitosamente!"
    print_success "Todos los builds han sido generados"
    print_status "Revisa BUILD_SUMMARY.md para más detalles"
}

# Ejecutar función principal
main "$@"
