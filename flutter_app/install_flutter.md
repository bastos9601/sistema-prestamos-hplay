# 🚀 Guía de Instalación de Flutter

## 📋 Requisitos Previos

### Windows
- Windows 10 o superior (64-bit)
- Git para Windows
- PowerShell 5.0 o superior
- Visual Studio 2019 o superior (para desarrollo Windows)

### macOS
- macOS 10.14 o superior
- Xcode 12.0 o superior
- CocoaPods
- Git

### Linux
- Ubuntu 18.04 o superior
- Git
- curl
- unzip
- xz-utils
- zip
- libglu1-mesa

## 🔧 Instalación de Flutter

### 1. Descargar Flutter SDK
```bash
# Clonar el repositorio de Flutter
git clone https://github.com/flutter/flutter.git -b stable

# Agregar Flutter al PATH
export PATH="$PATH:`pwd`/flutter/bin"
```

### 2. Verificar la instalación
```bash
flutter doctor
```

### 3. Instalar dependencias faltantes
```bash
# Android Studio
flutter doctor --android-licenses

# Xcode (macOS)
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
```

## 📱 Configuración para Android

### 1. Instalar Android Studio
- Descargar desde: https://developer.android.com/studio
- Instalar Android SDK
- Configurar variables de entorno:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### 2. Crear un dispositivo virtual
- Abrir Android Studio
- Tools > AVD Manager
- Create Virtual Device
- Seleccionar dispositivo y API level

### 3. Configurar build.gradle
```gradle
android {
    compileSdkVersion 34
    defaultConfig {
        minSdkVersion 21
        targetSdkVersion 34
    }
}
```

## 🍎 Configuración para iOS (macOS)

### 1. Instalar Xcode
- Descargar desde App Store
- Instalar Command Line Tools:
```bash
xcode-select --install
```

### 2. Configurar CocoaPods
```bash
sudo gem install cocoapods
cd ios
pod install
```

### 3. Configurar Info.plist
```xml
<key>NSCameraUsageDescription</key>
<string>Esta app necesita acceso a la cámara para escanear documentos</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>Esta app necesita acceso a la ubicación para registrar la ubicación del préstamo</string>
```

## 💻 Configuración para Desktop

### Windows
```bash
flutter config --enable-windows-desktop
flutter create --platforms=windows .
```

### macOS
```bash
flutter config --enable-macos-desktop
flutter create --platforms=macos .
```

### Linux
```bash
flutter config --enable-linux-desktop
flutter create --platforms=linux .
```

## 🌐 Configuración para Web

```bash
flutter config --enable-web
flutter create --platforms=web .
```

## 📦 Instalación del Proyecto

### 1. Clonar el repositorio
```bash
git clone [URL_DEL_REPOSITORIO]
cd flutter_app
```

### 2. Instalar dependencias
```bash
flutter pub get
```

### 3. Ejecutar la aplicación
```bash
# En dispositivo/emulador
flutter run

# En web
flutter run -d chrome

# En Windows
flutter run -d windows

# En macOS
flutter run -d macos

# En Linux
flutter run -d linux
```

## 🏗️ Generación de Builds

### APK para Android
```bash
# Debug
flutter build apk --debug

# Release
flutter build apk --release

# Por arquitectura
flutter build apk --split-per-abi
```

### App Bundle para Google Play
```bash
flutter build appbundle
```

### Web
```bash
flutter build web
# Los archivos se generan en build/web/
```

### Desktop
```bash
# Windows
flutter build windows

# macOS
flutter build macos

# Linux
flutter build linux
```

## 🔧 Configuración del Entorno

### Variables de entorno
```bash
# Agregar al .bashrc o .zshrc
export FLUTTER_ROOT=$HOME/flutter
export PATH=$PATH:$FLUTTER_ROOT/bin
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### Configuración de Flutter
```bash
# Habilitar todas las plataformas
flutter config --enable-web
flutter config --enable-windows-desktop
flutter config --enable-macos-desktop
flutter config --enable-linux-desktop

# Verificar configuración
flutter config
```

## 🧪 Testing

### Unit Tests
```bash
flutter test
```

### Integration Tests
```bash
flutter test integration_test/
```

### Widget Tests
```bash
flutter test test/widget_test.dart
```

## 📱 Emuladores y Dispositivos

### Android
```bash
# Listar dispositivos
flutter devices

# Ejecutar en dispositivo específico
flutter run -d [DEVICE_ID]
```

### iOS
```bash
# Listar simuladores
xcrun simctl list devices

# Ejecutar en simulador específico
flutter run -d [SIMULATOR_ID]
```

## 🚀 Deployment

### Google Play Store
1. Generar App Bundle: `flutter build appbundle`
2. Firmar con keystore
3. Subir a Google Play Console

### App Store
1. Generar IPA: `flutter build ipa`
2. Firmar con certificado de distribución
3. Subir a App Store Connect

### Web
1. Generar build: `flutter build web`
2. Subir a hosting (Firebase, Netlify, Vercel)

### Desktop
1. Generar ejecutable
2. Crear instalador
3. Distribuir por Microsoft Store, Mac App Store, etc.

## 🔍 Solución de Problemas

### Flutter doctor muestra errores
```bash
# Actualizar Flutter
flutter upgrade

# Limpiar cache
flutter clean
flutter pub get

# Verificar configuración
flutter doctor -v
```

### Problemas de dependencias
```bash
# Limpiar cache de pub
flutter pub cache clean

# Reinstalar dependencias
flutter pub get --force
```

### Problemas de build
```bash
# Limpiar build
flutter clean

# Reconstruir
flutter build apk --release
```

## 📚 Recursos Adicionales

- [Documentación oficial de Flutter](https://flutter.dev/docs)
- [Flutter Cookbook](https://flutter.dev/docs/cookbook)
- [Flutter Samples](https://github.com/flutter/samples)
- [Flutter Community](https://fluttercommunity.dev/)
- [Flutter Awesome](https://flutterawesome.com/)

## 🆘 Soporte

Si tienes problemas con la instalación:

1. Ejecutar `flutter doctor -v`
2. Revisar la documentación oficial
3. Buscar en Stack Overflow
4. Abrir issue en GitHub del proyecto
5. Contactar al equipo de desarrollo

---

**¡Feliz desarrollo con Flutter! 🎉**
