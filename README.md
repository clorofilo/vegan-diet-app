# 🍲 Planificador de Comidas Inteligente

Una aplicación web interactiva construida con **Streamlit** para ayudarte a planificar tus comidas diarias, permitiendo la sustitución inteligente de ingredientes basada en una tabla de equivalencias nutricionales.

## App en Streamlit Cloud
Puedes acceder directamente a la app a través del siguiente enlace:

[Accede a la app](https://vegan-diet.streamlit.app/)

## ✨ Características Principales
Esta aplicación se divide en tres módulos principales:

### 1. 📅 Planificador de Menús
- **Selecciona tu menú**: Elige un tipo de comida (Desayuno, Comida, Cena) y un plato específico de tu recetario.  
- **Visualiza la receta original**: Consulta los ingredientes y las cantidades base.  
- **Sustituye ingredientes**: Para cada ingrediente, elige un sustituto de la misma categoría nutricional. La aplicación calculará automáticamente la cantidad correcta del nuevo ingrediente.  
- **Guarda tu historial**: Registra la comida personalizada en un histórico, seleccionando la fecha y la hora, para llevar un seguimiento de lo que has comido.  

### 2. ⚖️ Calculadora de Equivalencias
- **Comparación rápida de ingredientes**: Introduce un ingrediente de origen, su peso, y un ingrediente de destino para descubrir la cantidad equivalente.  
- **Filtros avanzados**: Filtra por grupo de ingrediente y subcategoría para encontrar rápidamente lo que buscas.  

### 3. 📖 Histórico de Comidas
- **Visualiza tu registro**: Consulta todas las comidas que has guardado, ordenadas de la más reciente a la más antigua.  
- **Filtros avanzados**: Filtra tu historial por rango de fechas, tipo de comida, plato o grupo de ingrediente.  
- **Edición completa**: Modifica, añade o elimina registros directamente desde la aplicación. Los cambios se guardan permanentemente en tu archivo de histórico.  

---

## 🛠️ Tecnologías Utilizadas
- **Python**: Lenguaje principal de programación.  
- **Streamlit**: Para la creación de la interfaz de usuario web interactiva.  
- **Pandas**: Para la manipulación y análisis de los datos de las comidas y equivalencias.  

---

## 🚀 Instalación y Uso

Sigue estos pasos para ejecutar la aplicación en tu máquina local.

### Prerrequisitos
- Tener **Python 3.8** o superior instalado.  

### Pasos

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/tu-repositorio.git
   cd tu-repositorio
