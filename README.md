# MonaloVision - Backend Django (Inferencia IA)

Este es el repositorio oficial del backend para el proyecto **MonaloVision**, una plataforma inteligente de diagnóstico y clasificación del nivel de daño causado por la plaga del chinche del cacao (*Monalonion dissimulatum*) en frutos de cacao.

## 🔗 Repositorios del Proyecto
* **Backend Repository**: [https://github.com/JhosepSF/MonaloVision-Project-Back](https://github.com/JhosepSF/MonaloVision-Project-Back)
* **Frontend Repository**: [https://github.com/JhosepSF/MonaloVision-Project-Front](https://github.com/JhosepSF/MonaloVision-Project-Front)

---

## 🛠️ Tecnologías y Arquitectura

El backend está desarrollado sobre **Django** (Python 3.12) y está diseñado para ejecutar inferencias complejas de Deep Learning en menos de 4 segundos en CPU mediante el almacenamiento de modelos en memoria caché (Patrón Singleton).

### Pipeline de Inferencia de Inteligencia Artificial:
1. **Segmentación Morfológica (Mask R-CNN ResNet-50 FPN)**:
   * Recibe la foto enviada por el celular.
   * Detecta y extrae la máscara del fruto del cacao con menor distancia euclidiana al centro de la imagen.
   * Aplica un cierre morfológico (kernel 5x5) para limpiar contornos y vacíos.
   * Monta el cacao segmentado sobre un fondo negro sólido.
   * Rota la imagen **90 grados en sentido horario** (orientación idéntica a la del entrenamiento).
2. **Extracción de Características (ViT-Tiny Fine-Tuned)**:
   * Redimensiona la imagen a `224x224` y la normaliza.
   * Extrae el vector representativo multi-dimensional (192 canales).
3. **Clasificación (StandardScaler + SVM Classifier)**:
   * Normaliza las escalas del vector de entrada.
   * Ejecuta el modelo SVC de scikit-learn con estimación probabilística.
   * Clasifica en: `Sana` (Sin daño), `Daño Ligero`, `Daño Moderado` o `Daño Severo`.

---

## 📂 Estructura del Proyecto

```
backend/
├── backend/                  # Configuraciones raíz del proyecto Django
│   ├── settings.py           # Configuración general y habilitación de CORS
│   └── urls.py               # Enrutador principal de endpoints
├── classifier/               # Aplicación Django de clasificación
│   ├── model_loader.py       # Carga optimizada de modelos (Thread-safe Singleton)
│   ├── views.py              # Controlador del endpoint POST de clasificación
│   ├── modelos/              # Directorio con los archivos binarios de los modelos
│   │   ├── vit_tiny_extractor_finetuned_vittiny_svm_state_dict.pth
│   │   └── final_svm_classifier_vittiny_svm.pkl
│   └── urls.py               # Enrutador interno (/api/classify/)
├── requirements.txt          # Dependencias y librerías del backend
├── test_api.py               # Script de prueba rápida para desarrolladores
├── MANUAL_TECNICO.md         # Documentación técnica completa
└── MANUAL_USUARIO.md         # Guía detallada para el usuario
```

---

## 🚀 Instalación y Ejecución Local

### 1. Preparar el entorno virtual
```powershell
python -m venv .venv
# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Lanzar el Servidor en tu Red Local
```powershell
python manage.py runserver 0.0.0.0:8000
```
*Nota: El puerto por defecto es el `8000`. Al correr sobre `0.0.0.0`, el servidor aceptará llamadas desde el celular del agricultor conectado a la misma red WiFi.*

---

## 🧪 Pruebas Rápidas de Inferencia
Puedes ejecutar el cliente de prueba desarrollado en Python para simular una petición multipart desde tu computadora:
```powershell
# Sintaxis: python test_api.py <ruta_de_imagen>
python test_api.py ../Front/assets/1.jpeg
```
El script enviará la petición, imprimirá el reporte de métricas en consola y decodificará la respuesta del backend para guardar la imagen segmentada del cacao como `debug_segmented.jpg`.

---

**Desarrollado para la Tesis de Frank**  
**Contacto y Soporte**: Jhosep SF  
