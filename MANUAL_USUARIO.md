# Manual de Usuario - MonaloVision

## 📱 Guía de Uso de la Aplicación Móvil

---

## Índice
1. [Introducción](#1-introducción)
2. [Requisitos del Dispositivo](#2-requisitos-del-dispositivo)
3. [Instalación](#3-instalación)
4. [Inicio de la Aplicación](#4-inicio-de-la-aplicación)
5. [Funcionalidades Principales](#5-funcionalidades-principales)
6. [Preguntas Frecuentes](#6-preguntas-frecuentes)
7. [Solución de Problemas de Conexión](#7-solución-de-problemas-de-conexión)
8. [Soporte Técnico](#8-soporte-técnico)

---

## 1. Introducción

### ¿Qué es MonaloVision?

MonaloVision es una aplicación móvil diseñada específicamente para el sector cacaotero que te permite **diagnosticar e identificar el nivel de daño provocado por la plaga del chinche del cacao (*Monalonion dissimulatum*)** mediante el análisis fotográfico en tiempo real respaldado por Inteligencia Artificial.

### Ventajas de usar MonaloVision

* 🍃 **Fácil e intuitivo**: Interfaz moderna basada en tonos verdes suaves y otoñales de excelente visibilidad en el campo bajo luz solar directa.
* 🔍 **Precisión Científica**: Integra un extractor de características ViT-Tiny acoplado a un clasificador SVM robusto entrenado específicamente en cacao.
* 🤖 **Segmentación Avanzada**: Utiliza Mask R-CNN para aislar el fruto y remover hojas o malezas del fondo, mostrándote exactamente qué está evaluando el modelo.
* 📊 **Estadísticas de Confianza**: Muestra la distribución porcentual de probabilidad para cada nivel de afectación.
* 📂 **Historial Local**: Almacena de forma automática tus diagnósticos previos en la base de datos del celular para consultas rápidas sin requerir internet.

---

## 2. Requisitos del Dispositivo

* **Sistema Operativo**: Android 8.0 o superior / iOS 12.0 o superior
* **Cámara**: Cámara trasera funcional (con autoenfoque recomendado)
* **Conectividad**: Conexión WiFi o datos móviles activa en el mismo segmento de red local que el servidor de inferencia.
* **Almacenamiento**: 80 MB de espacio libre.

---

## 3. Instalación

### Opción A: Instalación desde APK (Android)
1. **Descargar el instalador APK** (`AppDeteccionCacao_v1.0.apk`) proporcionado.
2. **Habilitar fuentes externas**:
   * Ve a Ajustes → Seguridad.
   * Activa "Fuentes desconocidas" o "Instalar aplicaciones desconocidas".
3. **Instalación**:
   * Abre el archivo APK descargado.
   * Selecciona "Instalar" y concede los permisos.
4. **Listo**: Abre **MonaloVision** desde tu cajón de aplicaciones.

### Opción B: Ejecución en desarrollo con Expo Go
1. Descarga **Expo Go** desde Google Play Store o Apple App Store.
2. Abre tu terminal de desarrollo y corre `npx expo start`.
3. Escanea el código QR desde la app de Expo Go.

---

## 4. Inicio de la Aplicación

1. **Apertura**: Toca el ícono verde de **MonaloVision**.
2. **Permisos de Cámara**: Acepta la solicitud de acceso a la cámara. Esto es indispensable para capturar las fotografías de los frutos de cacao.
3. **Pantalla Principal**: Se cargará el panel de bienvenida con el logotipo oficial del cacao y dos opciones claras: **Analizar Cacao** y **Ver Historial**.

---

## 5. Funcionalidades Principales

### 5.1 Analizar Cacao y Clasificar Plaga

#### Paso 1: Acceder a la cámara
En la pantalla de bienvenida presiona el botón **"Analizar Cacao"** (icono de cámara con borde verde).

#### Paso 2: Consejos para una captura óptima (Muy Importante)
Para asegurar que la Inteligencia Artificial arroje un diagnóstico correcto, sigue estas pautas fotográficas:
* 🎯 **Encuadre**: Toma la foto de perfil del fruto de cacao, intentando que abarque el centro de la pantalla.
* 💡 **Iluminación**: Captura las fotos con buena iluminación natural. Evita sombras duras u oscuras sobre el fruto.
* 🌿 **Limpieza**: Remueve hojas o ramas del cacao que se interpongan entre la cámara y el fruto.
* 📏 **Distancia**: Mantén una distancia aproximada de 40 a 60 centímetros del fruto de cacao.

#### Paso 3: Captura o Selección
* **Tomar Foto**: Presiona *"Tomar Foto"* para activar la cámara del celular. Captura la imagen del cacao y confirma.
* **Subir de Galería**: Si ya tienes fotos tomadas previamente en el campo, presiona *"Subir de Galería"* y selecciona el archivo.

#### Paso 4: Ejecutar Análisis AI
1. Con la foto cargada en pantalla, presiona el botón naranja **"Analizar Fruto"**.
2. El sistema enviará la imagen al servidor y se mostrará el mensaje *"Ejecutando Modelos en Backend..."*. El procesamiento tomará entre 2 y 4 segundos.

#### Paso 5: Interpretación de Resultados
Al finalizar, aparecerá la pantalla de resultados con:
* **Diagnóstico Principal**: Clasificado en una de las 4 fases:
  * **Sana (Sin Daño)**: Fruto sano libre de plagas. (Verde)
  * **Daño Ligero**: Picaduras superficiales iniciales. (Amarillo)
  * **Daño Moderado**: Lesiones necróticas parciales visibles. (Naranja)
  * **Daño Severo**: Fruto ampliamente afectado y necrótico. (Rojo)
* **Badge de Confianza**: Muestra la seguridad del modelo (ej: `96.53%`).
* **Visualización Segmentada AI**: Si presionas el botón **"Segmentado AI"**, podrás ver el cacao aislado sobre un fondo negro. Esto te indica exactamente qué contornos de la cáscara del cacao utilizó la IA para su veredicto.
* **Distribución de Confianza**: Desglose con barras horizontales de colores indicativos del porcentaje asignado a cada nivel de daño.

---

### 5.2 Ver Historial

1. En el menú de bienvenida, presiona **"Ver Historial"**.
2. Se desplegará el listado completo de todos los diagnósticos ordenados cronológicamente (los más recientes primero).
3. Cada registro muestra:
   * La miniatura de la imagen del cacao.
   * El diagnóstico y color del nivel de daño.
   * El porcentaje de confianza obtenido.
   * La fecha y hora exacta del diagnóstico.
4. **Limpieza**: Si deseas vaciar el historial local, presiona el icono de basura rojo en la parte superior derecha de la pantalla.

---

## 6. Preguntas Frecuentes

### ¿El diagnóstico requiere internet?
Sí, la aplicación requiere de conexión para poder comunicarse con el backend de Django, ya que los modelos neuronales de inferencia (Mask R-CNN y ViT-Tiny) son sumamente robustos y se ejecutan en el servidor para evitar consumir el almacenamiento y procesador de tu celular.

### ¿Se guardan mis fotos en la nube?
No. Las fotos se envían temporalmente al backend para la inferencia morfológica y extracción de características y se eliminan inmediatamente del servidor una vez entregado el JSON de respuesta. Tu historial e imágenes se almacenan localmente de forma privada en el almacenamiento interno de la aplicación.

---

## 7. Solución de Problemas de Conexión

### Problema: "Error de conexión" al analizar
* **Causa**: La aplicación móvil no logra establecer comunicación con el servidor API REST.
* **Soluciones**:
  1. Verifica que tu PC y tu celular estén conectados a la **misma red WiFi**.
  2. Asegúrate de que el backend de Django esté encendido y escuchando en la IP correcta (`python manage.py runserver 0.0.0.0:8000`).
  3. Verifica que la IP definida en `Front/src/services/api.ts` coincida exactamente con la IP activa de tu computadora.

---

## 8. Soporte Técnico

* **Repositorio Móvil**: https://github.com/JhosepSF/MonaloVision-Project-Front
* **Repositorio Backend**: https://github.com/JhosepSF/MonaloVision-Project-Back

---

**Versión del Manual**: 2.0  
**Fecha de Publicación**: Junio 2026  
**Desarrollado por**: Jhosep SF & Frank  
**Plataforma**: MonaloVision App  
