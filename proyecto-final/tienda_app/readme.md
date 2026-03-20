# Proyecto Tienda Django
--------------------------------------------------------------------------

Este proyecto implementa una tienda con categorías, productos, ventas,
detalleventa y perfiles de usuario.

---------------------------------------------------------------------------

## 🚀 Instalación de dependencias

1. Clona el repositorio:
   ```bash
   git clone https://github.com/usuario/proyecto-final.git
   cd proyecto-final

2. Crea un entorno virtual
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\Activate.ps1     # Windows

3. Instala las dependencias
pip install -r requirements.txt

4. Configuración de variables de entorno
Crea un archivo .env en la raíz del proyecto 
con los parámetros de conexión a la base de datos.Ejemplo:

DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=tienda_db
DB_PORT=3306

5. Aplica las migraciones :
python manage.py makemigrations
python manage.py migrate


6. Levanta el servidor
python manage.py runserver 

7. Ejecutar la carga de datos desde CSV
python .\importar_csv.py