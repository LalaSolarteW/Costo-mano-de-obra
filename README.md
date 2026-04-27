# 📊 Informe de Costos

Este proyecto consiste en la construcción de un informe interactivo de costos, desarrollado en **Dash (Plotly)**, permite analizar los costos manejados en distintas secciones de la empresa a partir de datos previamente procesados.

---

## 🚀 Descripción del proyecto

El objetivo principal es consolidar, limpiar y visualizar información de costos proveniente de múltiples fuentes, generando un dashboard dividido en tres secciones principales:

1. **Procesos de Producción**
2. **Informe de Proveedores**
3. **Análisis de Insumos y MP**

Cada sección se alimenta de procesos de limpieza de datos independientes y presenta visualizaciones interactivas para facilitar el análisis.

---

## 🗂️ Estructura del proyecto

```
Costo mano de obra/
│
├── assets/                    # En esta carpeta encuentras el archivo CSS para definir el estilo del informe en Dash
├── Costeos/                   # Archivos fuente de Costeos por OP-D de los últimos 6 meses
├── Insumos y MP/              # Archivos fuente para la página de insumos y materias primas
├── Proveedores y clientes/    # Archivos fuente de proveedores y clientes
├── nginx/                     # Configuración para despliegue de servidor en docker
│
├── app.py                     # Aplicación principal en Dash / Informe con las 3 páginas 
├── graficas.py                # Definición de gráficos de la primera página del informe "procesos de producción"
├── graficas.ipynb             # Exploración y prototipos de gráficos
│
├── data_cleaning_costeos.ipynb        # Limpieza y unión de datos de costeos (de aquí sale el excel de la primera página del informe)
├── data_cleaning_prov_y_clien.ipynb   # Limpieza de datos de proveedores (de aquí sale el excel de la segunda página del informe)
│
├── df_dinall.xlsx             # Dataset final de procesos de producción
├── dffinn.xlsx                # Dataset final de proveedores y clientes
│
├── docker-compose.yml         # Orquestación de contenedores
├── Dockerfile                 # Configuración de imagen Docker
│
├── index.html                 # Versión HTML inicial (no usada actualmente)
├── logo.png                   # logo para el HTML
└── README.md                  # README
```

---

## ⚙️ Flujo de datos

### 🔹 Procesos de Producción

1. Los datos se obtienen de archivos en la carpeta **Costeos/**
2. Se limpian y transforman en:

   * `data_cleaning_costeos.ipynb`
3. Se genera el dataset final:

   * `df_dinall.xlsx`
4. Este dataset es consumido por:

   * `graficas.py` (gráficos en Plotly)
5. Finalmente:

   * `app.py` importa estos gráficos y los muestra en Dash

---

### 🔹 Informe de Proveedores

1. Los datos provienen de:

   * `Proveedores y clientes/`
2. Se procesan en:

   * `data_cleaning_prov_y_clien.ipynb`
3. Se genera:

   * `dffinn.xlsx`
4. Los gráficos se construyen directamente en:

   * `app.py`

---

## 📈 Visualización

El dashboard está desarrollado en **Dash**, utilizando **Plotly** para las visualizaciones.

Incluye:

* Comparación de costos por proveedor
* Análisis de procesos de producción
* Identificación de oportunidades de ahorro

---

## 🐳 Ejecución con Docker

El proyecto está completamente dockerizado, lo que permite ejecutarlo fácilmente sin necesidad de configurar dependencias manualmente.

### ▶️ Ejecutar el proyecto

```bash
docker-compose up -d --build
```

Luego abre tu navegador en:

```
http://localhost:8050
```

---

## 🧪 Notas adicionales

* El archivo `graficas.ipynb` contiene versiones exploratorias de los gráficos y un informe HTML inicial (ya no utilizado, pero conservado como referencia).
* Los archivos `.xlsx` son el resultado de procesos de limpieza y consolidación de datos.
* La carpeta `nginx/` está preparada para despliegues más avanzados.

---

## 🛠️ Tecnologías utilizadas

* Python
* Dash
* Plotly
* Pandas
* Docker
* Nginx

---

## 📌 Estado del proyecto

En desarrollo 🚧
Estructura funcional y lista para mejoras en visualización y despliegue.

---
