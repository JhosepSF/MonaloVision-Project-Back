# Manual Técnico - MonaloVision

## 📚 Índice
1. [Introducción](#1-introducción)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Componentes del Frontend (Móvil)](#3-componentes-del-frontend-móvil)
4. [Componentes del Backend (API Django)](#4-componentes-del-backend-api-django)
5. [Modelos de Inteligencia Artificial](#5-modelos-de-inteligencia-artificial)
6. [API REST & Comunicación](#6-api-rest--comunicación)
7. [Instalación y Configuración](#7-instalación-y-configuración)
8. [Despliegue con EAS](#8-despliegue-con-eas)
9. [Mantenimiento y Soporte](#9-mantenimiento-y-soporte)

---

## 1. Introducción

### 1.1 Propósito del Documento
Este manual técnico describe en detalle la arquitectura, tecnologías, flujos de datos y modelos del sistema **MonaloVision**, una plataforma compuesta por una aplicación móvil multiplataforma (React Native) y un servidor backend (Django) para la clasificación automática de daño por la plaga del chinche del cacao (*Monalonion dissimulatum*) mediante visión artificial.

### 1.2 Alcance
El sistema comprende:
* **Frontend Móvil**: Desarrollado en React Native con Expo (TypeScript).
* **Backend Inferencia**: Desarrollado en Django con PyTorch, Scikit-learn y OpenCV, ejecutando la precarga de modelos para tiempos de respuesta menores a 4 segundos en CPU.

### 1.3 Repositorios del Proyecto
* **Frontend**: [https://github.com/JhosepSF/MonaloVision-Project-Front](https://github.com/JhosepSF/MonaloVision-Project-Front)
* **Backend**: [https://github.com/JhosepSF/MonaloVision-Project-Back](https://github.com/JhosepSF/MonaloVision-Project-Back)

---

## 2. Arquitectura del Sistema

### 2.1 Arquitectura General

```
┌────────────────────────┐
│    Aplicación Móvil    │
│  (React Native - Expo) │
└───────────┬────────────┘
            │
            │ HTTP / Multipart POST (Imagen)
            │
┌───────────▼────────────┐
│      API Backend       │
│    (Django - 8000)     │
└───────────┬────────────┘
            │
     ┌──────┴──────┐
     │             │
┌────▼────┐   ┌────▼────┐
│ Modelos │   │  SQLite │
│   IA    │   │    DB   │
└─────────┘   └─────────┘
```

### 2.2 Flujo de Procesamiento en el Backend

```
Imagen Recibida → Mask R-CNN → Crop + Fondo Negro → Rotación 90° → ViT-Tiny Extractor → SVM Classifier → Respuesta JSON
```

---

## 3. Componentes del Frontend (Móvil)

### 3.1 Tecnologías Utilizadas

| Biblioteca / Herramienta | Versión | Propósito |
| :--- | :--- | :--- |
| **React Native** | 0.81+ | Framework base móvil |
| **Expo SDK** | 54.0+ | Plataforma de desarrollo y empaquetado |
| **TypeScript** | 5.9+ | Lenguaje tipado |
| **Axios** | 1.10+ | Cliente de peticiones HTTP |
| **AsyncStorage** | 2.2.0 | Persistencia de datos locales |
| **Expo Camera** | 17.0+ | Captura fotográfica nativa |

### 3.2 Estructura del Código Fuente

```
Front/
├── assets/                    # Recursos visuales (logo.webp, iconos)
├── src/
│   ├── components/            # Componentes globales de interfaz
│   │   ├── CustomHeader.tsx   # Cabecera con fondo verde forestal
│   │   └── Footer.tsx         # Pie con derechos de MonaloVision
│   ├── navigation/            # Sistema de navegación
│   │   └── AppNavigator.tsx   # Stack Navigator móvil
│   ├── screens/               # Pantallas (Vistas)
│   │   ├── MenuRegistroScreen.tsx # Bienvenida y accesos principales
│   │   ├── TomarFotoScreen.tsx    # Captura, análisis y toggle AI
│   │   └── HistorialScreen.tsx    # Listado de diagnósticos guardados
│   └── services/              # Lógica externa
│       └── api.ts             # Cliente Axios e integración local
├── app.json                   # Propiedades de Expo y EAS Link (bc31b4b7...)
└── package.json               # Dependencias npm
```

### 3.3 Almacenamiento Local (Historial)
Se implementa una base de datos local en caché mediante `@react-native-async-storage/async-storage` bajo la clave `'historial_estimaciones'`.

**Esquema de Datos (TypeScript)**:
```typescript
type DiagnosticoRecord = {
  id: string;
  fotoUri: string;
  clase: string;          // 'DañoLigero' | 'DañoModerado' | 'DañoSevero' | 'Sana'
  confianza: number;      // 0.0 to 1.0
  segmentedImageB64: string | null; // Imagen segmentada por Mask R-CNN en Base64
  fecha: string;          // ISOString
};
```

---

## 4. Componentes del Backend (API Django)

### 4.1 Tecnologías y Entorno

| Dependencia | Propósito |
| :--- | :--- |
| **Django** | Servidor API REST robusto y extensible |
| **django-cors-headers** | Habilitación de llamadas cruzadas (CORS) para el frontend |
| **PyTorch & Torchvision** | Carga y ejecución del modelo Mask R-CNN |
| **timm** | Carga de la arquitectura de ViT-Tiny |
| **Scikit-learn** | Pipeline de normalización StandardScaler y clasificador SVM |
| **OpenCV-Python** | Transformación de contornos, remoción morfológica y rotaciones |

### 4.2 Arquitectura de Carga y Optimización (Singleton)
Para evitar recargas constantes y retrasos críticos en peticiones HTTP, el backend implementa una clase thread-safe `ModelManager` (`classifier/model_loader.py`) que precarga los tres modelos al inicializar el servidor:

```python
class ModelManager:
    _instance = None
    _lock = threading.Lock()
    # Inicializa Mask R-CNN, ViT-Tiny y SVM a nivel de clase para actuar como Singleton
```

---

## 5. Modelos de Inteligencia Artificial

### 5.1 Preprocesamiento: Segmentación con Mask R-CNN ResNet-50 FPN
* **Estrategia**: Identifica los objetos en la foto, calcula el centro de masa del cacao y extrae la máscara con menor distancia euclidiana al centro de la imagen.
* **Operación Morfológica**: Se ejecuta un cierre morfológico con un kernel de `5x5` (`cv2.morphologyEx(..., cv2.MORPH_CLOSE, kernel)`) para limpiar vacíos de contorno.
* **Fondo Negro y Orientación**: Aplica la máscara sobre un lienzo negro (`np.where`) y realiza una rotación de **90° en sentido horario** (`cv2.ROTATE_90_CLOCKWISE`) para que coincida exactamente con la postura utilizada en el entrenamiento.

### 5.2 Extracción de Características: ViT-Tiny Fine-Tuned
* **Modelo**: `vit_tiny_patch16_224.augreg_in21k`
* **Configuración**: Se redimensiona la imagen a `224x224`, se normaliza en base a la media de ImageNet `[0.485, 0.456, 0.406]` y desviación `[0.229, 0.224, 0.225]`. Retorna un embedding vectorial de **192 dimensiones**.

### 5.3 Clasificación: SVM (Support Vector Machine)
* **Pipeline**: Se alimenta el vector a `StandardScaler()` y posteriormente al clasificador `SVC(probability=True)`.
* **Clases de salida**:
  1. `DañoLigero` (Clase 0)
  2. `DañoModerado` (Clase 1)
  3. `DañoSevero` (Clase 2)
  4. `Sana` (Clase 3)

---

## 6. API REST & Comunicación

### 6.1 Endpoint de Clasificación

* **Ruta**: `POST /api/classify/`
* **Tipo**: `multipart/form-data`
* **Parámetros**:
  * `image`: Archivo de imagen (JPEG/PNG)

* **Respuesta de Éxito (`200 OK`)**:
```json
{
  "class": "DañoLigero",
  "confidence": 0.5816,
  "probabilities": {
    "DañoLigero": 0.5816,
    "DañoModerado": 0.2777,
    "DañoSevero": 0.1227,
    "Sana": 0.0180
  },
  "segmentation_success": true,
  "segmented_image": "/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "latency_ms": 3071
}
```

---

## 7. Instalación y Configuración

### 7.1 Configuración de Servidor Django (Backend)
1. **Instalar el Entorno Virtual y dependencias**:
   ```powershell
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Lanzar el Servidor en tu Red Local**:
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```

### 7.2 Configuración del Frontend
1. **Instalar paquetes**:
   ```powershell
   cd Front
   npm install
   ```
2. **Definir la IP de tu servidor** en `Front/src/services/api.ts`:
   ```typescript
   const api = axios.create({
     baseURL: 'http://192.168.172.7:8000', // Modifica por la IP activa de tu PC
   });
   ```
3. **Lanzar la aplicación**:
   ```powershell
   npx expo start
   ```

---

## 8. Despliegue con EAS
El proyecto móvil se encuentra enlazado a la plataforma Expo Application Services (EAS) con el ID: `bc31b4b7-72f2-4716-8757-ca96683719ad`.

**Para compilar un instalador nativo para Android (APK)**:
```powershell
# Instalar EAS CLI de manera global
npm install -g eas-cli
# Iniciar sesión en tu cuenta
eas login
# Ejecutar la compilación nativa en la nube
eas build --platform android --profile production
```

---

**Versión del Manual**: 2.0  
**Fecha de Actualización**: Junio 2026  
**Desarrollado para**: Tesis de Frank  
**Módulo de Clasificación**: ViT-Tiny + SVM con Segmentación Mask R-CNN  
