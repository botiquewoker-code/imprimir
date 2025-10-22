# Imagen base de Python
FROM python:3.10

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8080 (Google Cloud Run usa este)
EXPOSE 8080

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
