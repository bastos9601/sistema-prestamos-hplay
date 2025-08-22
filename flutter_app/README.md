# 📱 Sistema de Préstamos - Aplicación Flutter

## 🎯 Descripción
Aplicación móvil multiplataforma del Sistema de Préstamos desarrollada en Flutter.

## 📱 Plataformas Soportadas
- ✅ **Android** (APK)
- ✅ **iOS** (App Store)
- ✅ **Web** (Navegador)
- ✅ **Windows** (Desktop)
- ✅ **macOS** (Desktop)
- ✅ **Linux** (Desktop)

## 🛠️ Tecnologías
- **Frontend**: Flutter 3.x
- **Backend**: API REST (Flask)
- **Base de Datos**: SQLite local + API remota
- **Estado**: Provider/Bloc
- **HTTP**: Dio/HTTP
- **Almacenamiento**: SharedPreferences + SQLite

## 📋 Características
- 🔐 Autenticación segura
- 👥 Gestión de usuarios y roles
- 💰 Gestión de préstamos
- 👤 Gestión de clientes
- 💳 Gestión de pagos
- 📊 Reportes y estadísticas
- 📄 Generación de pagarés
- 📧 Recuperación de contraseña
- 🔄 Sincronización offline/online
- 🌙 Modo oscuro/claro
- 📱 Diseño responsive

## 🚀 Instalación

### Requisitos
- Flutter SDK 3.x
- Dart SDK 3.x
- Android Studio / VS Code
- Git

### Pasos
```bash
# Clonar el repositorio
git clone [URL_DEL_REPO]

# Entrar al directorio
cd flutter_app

# Instalar dependencias
flutter pub get

# Ejecutar en dispositivo
flutter run

# Generar APK
flutter build apk

# Generar App Bundle
flutter build appbundle

# Generar para Web
flutter build web

# Generar para Windows
flutter build windows

# Generar para macOS
flutter build macos

# Generar para Linux
flutter build linux
```

## 📱 Generación de APK
```bash
# APK de debug
flutter build apk --debug

# APK de release
flutter build apk --release

# APK dividido por arquitectura
flutter build apk --split-per-abi
```

## 🌐 Generación para Web
```bash
flutter build web
# Los archivos se generan en build/web/
```

## 💻 Generación para Desktop
```bash
# Windows
flutter build windows

# macOS
flutter build macos

# Linux
flutter build linux
```

## 📦 Estructura del Proyecto
```
flutter_app/
├── lib/
│   ├── main.dart
│   ├── app.dart
│   ├── config/
│   ├── models/
│   ├── services/
│   ├── providers/
│   ├── screens/
│   ├── widgets/
│   └── utils/
├── assets/
│   ├── images/
│   ├── icons/
│   └── fonts/
├── android/
├── ios/
├── web/
├── windows/
├── macos/
├── linux/
└── pubspec.yaml
```

## 🔧 Configuración

### Android
- `android/app/build.gradle` - Configuración de build
- `android/app/src/main/AndroidManifest.xml` - Permisos y configuración

### iOS
- `ios/Runner/Info.plist` - Configuración de la app
- `ios/Runner.xcodeproj` - Proyecto Xcode

### Web
- `web/index.html` - Página principal
- `web/manifest.json` - PWA manifest

## 📱 Características Móviles
- 🔄 Pull to refresh
- 📱 Gestos táctiles
- 📍 Geolocalización
- 📷 Cámara para documentos
- 📁 Selección de archivos
- 🔔 Notificaciones push
- 📊 Gráficos interactivos
- 🖨️ Impresión móvil

## 🌐 Características Web
- 📱 PWA (Progressive Web App)
- 🔄 Service Worker
- 📊 Offline support
- 🎨 Responsive design
- 🔍 SEO optimizado

## 💻 Características Desktop
- 🖱️ Soporte de mouse
- ⌨️ Atajos de teclado
- 🪟 Múltiples ventanas
- 📁 Drag & drop
- 🖨️ Impresión nativa

## 🚀 Deployment

### Android
- Google Play Store
- APK directo
- F-Droid

### iOS
- App Store
- TestFlight

### Web
- Firebase Hosting
- Netlify
- Vercel
- GitHub Pages

### Desktop
- Microsoft Store
- Mac App Store
- Snap Store
- Flathub

## 📊 Métricas de Build
- **APK Android**: ~15-25 MB
- **iOS App**: ~20-30 MB
- **Web**: ~2-5 MB
- **Windows**: ~25-35 MB
- **macOS**: ~30-40 MB
- **Linux**: ~25-35 MB

## 🔒 Seguridad
- 🔐 Autenticación JWT
- 🔒 Encriptación local
- 🛡️ Certificados SSL
- 🔑 Biometría (huella/face)
- 🚫 Jailbreak/root detection

## 📈 Performance
- ⚡ Carga rápida
- 🔄 Lazy loading
- 📱 Optimización móvil
- 💾 Cache inteligente
- 🚀 Compilación AOT

## 🧪 Testing
```bash
# Unit tests
flutter test

# Integration tests
flutter test integration_test/

# Widget tests
flutter test test/widget_test.dart
```

## 📚 Documentación
- [Flutter Docs](https://flutter.dev/docs)
- [Dart Docs](https://dart.dev/guides)
- [Material Design](https://material.io/design)

## 🤝 Contribución
1. Fork el proyecto
2. Crea una rama feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia
MIT License - Ver LICENSE para más detalles

## 📞 Soporte
- 📧 Email: soporte@prestamos.com
- 💬 Discord: [Link del servidor]
- 📱 WhatsApp: +1234567890
- 🌐 Web: https://prestamos.com/soporte

---
**Desarrollado con ❤️ usando Flutter**
