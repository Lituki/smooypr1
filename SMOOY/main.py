print ("El server está arrancando...")
import secrets
from fastapi import FastAPI, HTTPException, Path, Query, File, Form, UploadFile, Depends, Header, Security, Request, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Path, Body, Query, HTTPException, Depends
from typing import List, Optional, Dict, Any
import os
import time
import shutil
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

import uuid
from passlib.context import CryptContext

# Configuración JWT - USAR EXACTAMENTE ESTOS VALORES
SECRET_KEY = "tu_clave_secreta_aqui"  # IMPORTANTE: Usa EXACTAMENTE esta clave
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1  # 24 horas

# Configuración de seguridad para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para autenticación con token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos para tokens JWT
class Token(BaseModel):
    access_token: str
    token_type: str

class Usuario(BaseModel):
    usuario: str
    contrasena: str  
    nombre: str
    apellido: str
    rol: str
    establecimiento_id: Optional[int] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

class AvisoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    categoria: str
    establecimientoId: int
    usuarioId: int
    fechaCreacion: str  # Usando datetime para validación automática

class AvisoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    establecimientoId: Optional[int] = Field(None, alias="establecimientoId")
    usuarioId: Optional[int] = Field(None, alias="usuarioId")
    estado: Optional[str] = None  # Nuevo campo para el estado

    class Config:
        allow_population_by_field_name = True

# Estados válidos para los avisos
ESTADOS_AVISOS = [
    'Pendiente', 
    'En Proceso', 
    'Verificado', 
    'Rechazado', 
    'Completado'
]

# Conexión a la base de datos
def conectar_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='smooydb',  # Nombre correcto según archivo SQL
            user='root',         # Usuario por defecto en XAMPP/WAMP
            password='',         # Contraseña vacía por defecto
            port=3306
        )
        if connection.is_connected():
            print("Conexión a MySQL establecida correctamente")
            return connection
    except Error as e:
        print(f"Error al conectarse a MySQL: {e}")
        return None

def verificar_tablas():
    """
    Verifica que las tablas necesarias existan y tengan las columnas requeridas
    """
    conexion = conectar_db()
    if (conexion is None):
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = None
    try:
        cursor = conexion.cursor()
        
        # Verificar tabla Establecimientos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Establecimientos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            direccion VARCHAR(255),
            tipo VARCHAR(100),
            estado VARCHAR(50)
        )
        """)
        
        # Verificar tabla proceso_comentarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS proceso_comentarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            proceso_id INT NOT NULL,
            usuario_id INT NOT NULL,
            comentario TEXT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Verificar si existe la columna fecha_creacion en proceso_comentarios
        cursor.execute("SHOW COLUMNS FROM proceso_comentarios LIKE 'fecha_creacion'")
        if not cursor.fetchone():
            print("Añadiendo columna fecha_creacion a proceso_comentarios")
            cursor.execute("ALTER TABLE proceso_comentarios ADD COLUMN fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # Verificar tabla proceso_imagenes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS proceso_imagenes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            proceso_id INT NOT NULL,
            usuario_id INT NOT NULL,
            ruta_imagen VARCHAR(255) NOT NULL,
            nombre_imagen VARCHAR(255) NOT NULL,
            fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Verificar si existe la columna fecha_subida en proceso_imagenes
        cursor.execute("SHOW COLUMNS FROM proceso_imagenes LIKE 'fecha_subida'")
        if not cursor.fetchone():
            print("Añadiendo columna fecha_subida a proceso_imagenes")
            cursor.execute("ALTER TABLE proceso_imagenes ADD COLUMN fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # Verificar tabla avisos con el campo estado
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS avisos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            descripcion TEXT,
            establecimiento_id INT NOT NULL,
            usuario_id INT NOT NULL,
            estado VARCHAR(50) DEFAULT 'Pendiente',
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Verificar si existe la columna estado en avisos
        cursor.execute("SHOW COLUMNS FROM avisos LIKE 'estado'")
        if not cursor.fetchone():
            print("Añadiendo columna estado a avisos")
            cursor.execute("ALTER TABLE avisos ADD COLUMN estado VARCHAR(50) DEFAULT 'Pendiente'")
        
        conexion.commit()
        print("Tablas verificadas y actualizadas correctamente")
        
    except Error as e:
        print(f"Error al verificar tablas: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def inicializar_db():
    """Función para inicializar la base de datos"""
    verificar_tablas()
    
    # Otras tareas de inicialización si son necesarias
    print("Base de datos inicializada correctamente")
    
# Llamar a la función de inicialización una sola vez
inicializar_db()

app = FastAPI()

# Ejecutar verificación de tablas al iniciar
verificar_tablas()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desarrollo, en producción especifica dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Primero, definimos correctamente las rutas públicas
PUBLIC_PATHS = [
    "/login", 
    "/registro",
    "/debug/headers",
    "/verify-token",
    "/docs",           # Documentación Swagger
    "/openapi.json",   # Esquema OpenAPI para Swagger
    "/redoc",          # Documentación ReDoc
    "/static",         # Archivos estáticos
    # Añadir estas rutas para pruebas iniciales (eliminar en producción)
    "/procesos",       # Ruta principal de procesos
    "/avisos",         # Ruta principal de avisos 
    "/establecimientos" # Ruta de establecimientos
]

# 4. ELIMINA TODOS los demás middlewares verify_jwt_token y usa solo este
@app.middleware("http")
async def verify_jwt_token(request: Request, call_next):
    # Lista completa de rutas públicas
    public_paths = [
        "/login", 
        "/docs",
        "/openapi.json",
        "/redoc",
        "/static",
        "/debug/headers",
        "/verify-token",
        "/api-status"
    ]
    
    path = request.url.path
    
    # Si la ruta es pública o comienza con uno de los prefijos públicos, permitir acceso sin token
    if path in public_paths or any(path.startswith(prefix) for prefix in ["/static/", "/docs/"]):
        print(f"Acceso a ruta pública: {path}")
        return await call_next(request)
    
    # Para rutas protegidas, verificar token JWT
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        print(f"🔒 Acceso denegado a {path}: No token proporcionado o formato incorrecto")
        return JSONResponse(
            status_code=401,
            content={"detail": "No se proporcionó un token válido"}
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # ⚠️ IMPORTANTE: Usar la SECRET_KEY definida al inicio del archivo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # print(f"✅ Token válido para usuario {payload.get('sub')} accediendo a {path}")
        
        request.state.user = {
            "username": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "role": payload.get("role")
        }
    except JWTError as e:
        print(f"❌ Token inválido: {str(e)}")
        return JSONResponse(
            status_code=401,
            content={"detail": f"Token inválido: {str(e)}"}
        )
    
    return await call_next(request)

# Definimos un modelo de datos para la solicitud de login
class LoginRequest(BaseModel):
    usuario: str
    contraseña: str

# Reemplaza la definición actual de la clase Proceso
class Proceso(BaseModel):
    tipo_proceso: Optional[str] = Field(None, alias="tipoProceso")  # Opcional ahora
    descripcion: Optional[str] = None
    establecimiento_id: Optional[int] = Field(None, alias="establecimientoId")
    usuario_id: Optional[int] = Field(None, alias="usuarioId")
    frecuencia: Optional[str] = None
    horario: Optional[str] = None
    fecha_inicio: Optional[str] = Field(None, alias="fechaInicio") 
    fecha_fin: Optional[str] = Field(None, alias="fechaFin")
    estado: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Permitir campos adicionales

# Definimos modelos para comentarios e imágenes
class ProcesoComentario(BaseModel):
    proceso_id: int
    usuario_id: int  # Añade este campo
    comentario: str

class ProcesoImagen(BaseModel):
    id: Optional[int] = None
    proceso_id: int
    usuario_id: int
    ruta_imagen: str
    nombre_imagen: str
    fecha_subida: Optional[str] = None

# Definimos modelos para avisos
class AvisoBase(BaseModel):
    nombre: str
    categoria: str
    descripcion: str
    establecimientoId: int  # Cambiado de establecimiento_id
    usuarioId: int          # Cambiado de usuario_id

    class Config:
        orm_mode = True

class AvisoCreate(BaseModel):
    nombre: str
    categoria: str
    descripcion: str
    establecimientoId: int = Field(alias="establecimientoId")
    usuarioId: int = Field(alias="usuarioId")

    class Config:
        allow_population_by_field_name = True

# Modifica la clase Aviso para incluir estado
class Aviso(AvisoBase):
    id: int
    fechaCreacion: datetime  # Cambiado de str a datetime
    estado: Optional[str] = "Pendiente"  # Estado por defecto

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S')
        }

# Directorio para almacenar imágenes
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Montar el directorio de uploads como estático
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Funciones para manejar tokens JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        raise credentials_exception

# Middleware para verificar token en las solicitudes
async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)

# Endpoint para obtener token (puedes usarlo para pruebas o como alternativa)
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s", 
                      (form_data.username, form_data.password))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": usuario.get("usuario"), 
                  "user_id": usuario.get("ID"), 
                  "role": usuario.get("Rol")},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Modificar el endpoint de login existente para incluir JWT
def verificar_contraseña(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Reemplaza el endpoint de login con esta versión mejorada

import hashlib  # Or whatever hashing library you're using

def verify_password(plain_password, stored_password):
    """Verify the password correctly based on your storage method."""
    # If using plain text (not recommended)
    if plain_password == stored_password:
        return True
    
    # If using hashed passwords (adjust according to your actual hashing method)
    # hashed_input = hashlib.sha256(plain_password.encode()).hexdigest()
    # return hashed_input == stored_password
    
    return False

@app.post("/login")
async def login(login_data: LoginRequest):
    # Verificación inicial de datos
    if not login_data.usuario or not login_data.contraseña:
        return {
            "success": False,
            "message": "Usuario y contraseña son requeridos"
        }
    
    print(f"Intento de login para: {login_data.usuario}")
    
    # Conectar a la base de datos
    conexion = conectar_db()
    if conexion is None:
        print("Error: No se pudo conectar a la base de datos")
        return {
            "success": False,
            "message": "Error interno del servidor. Intente más tarde."
        }
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Buscar usuario en la base de datos
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (login_data.usuario,))
        usuario = cursor.fetchone()
        
        if not usuario:
            print(f"Usuario no encontrado: {login_data.usuario}")
            return {
                "success": False,
                "message": "Usuario o contraseña incorrectos"
            }
        
        print(f"Usuario encontrado: {login_data.usuario}, ID: {usuario['ID']}, Rol: {usuario['Rol']}")
        
        # Determine the correct column name for password
        password_column = None
        for possible_column in ['Contraseña', 'contraseña', 'contrasena', 'password']:
            if possible_column in usuario:
                password_column = possible_column
                break
        
        if not password_column:
            print("Error: No se pudo encontrar la columna de contraseña")
            return {
                "success": False,
                "message": "Error de configuración del servidor"
            }
        
        # Password verification - with logging for debugging
        stored_password = usuario[password_column]
        print(f"Contraseña almacenada: {stored_password[:6]}... (primeros caracteres)")
        
        # ELIMINADO: ya no hay bypass para usuarios de prueba
        
        # Better error handling for bcrypt verification
        try:
            # Check if the stored password looks like a bcrypt hash
            if stored_password.startswith('$2'):
                # It's a bcrypt hash, use verify
                is_password_correct = pwd_context.verify(login_data.contraseña, stored_password)
            else:
                # Plain text comparison (fallback, not recommended)
                is_password_correct = (login_data.contraseña == stored_password)
            
            print(f"Verificación de contraseña: {is_password_correct}")
        except Exception as e:
            print(f"Error en verificación de contraseña: {str(e)}")
            is_password_correct = False
        
    except Exception as e:
        print(f"ERROR EN LOGIN: {str(e)}")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Buscar usuario en la base de datos
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (login_data.usuario,))
        usuario = cursor.fetchone()
        
        if not usuario:
            print(f"Usuario no encontrado: {login_data.usuario}")
            return {
                "success": False,
                "message": "Usuario o contraseña incorrectos"
            }
        
        print(f"Usuario encontrado: {login_data.usuario}, ID: {usuario['ID']}, Rol: {usuario['Rol']}")
        
        # Determine the correct column name for password
        password_column = None
        for possible_column in ['Contraseña', 'contraseña', 'contrasena', 'password']:
            if possible_column in usuario:
                password_column = possible_column
                break
        
        if not password_column:
            print("Error: No se pudo encontrar la columna de contraseña")
            return {
                "success": False,
                "message": "Error de configuración del servidor"
            }
        
        # Password verification - with logging for debugging
        stored_password = usuario[password_column]
        print(f"Contraseña almacenada: {stored_password[:6]}... (primeros caracteres)")
        
        # Special handling for test users
        if login_data.usuario in ["AdminSMOOY", "StaffSMOOY"] and login_data.contraseña == "SMOOY":
            is_password_correct = True
            print(f"Bypass de contraseña para usuario de prueba: {login_data.usuario}")
        else:
            # Better error handling for bcrypt verification
            try:
                # Check if the stored password looks like a bcrypt hash
                if stored_password.startswith('$2'):
                    # It's a bcrypt hash, use verify
                    is_password_correct = pwd_context.verify(login_data.contraseña, stored_password)
                else:
                    # Plain text comparison (fallback, not recommended)
                    is_password_correct = (login_data.contraseña == stored_password)
                
                print(f"Verificación de contraseña: {is_password_correct}")
            except Exception as e:
                print(f"Error en verificación de contraseña: {str(e)}")
                is_password_correct = False
        
        if not is_password_correct:
            return {
                "success": False,
                "message": "Usuario o contraseña incorrectos"
            }
        
        # Generar token JWT
        from jose import jwt
        from datetime import datetime, timedelta
        
        SECRET_KEY = "tu_clave_secreta_aqui"
        ALGORITHM = "HS256"
        
        expires = datetime.utcnow() + timedelta(minutes=1440)  # 24 horas
        to_encode = {
            "sub": usuario["usuario"],
            "user_id": usuario["ID"],
            "role": usuario["Rol"],
            "exp": expires
        }
        
        try:
            access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            print(f"Token JWT generado correctamente para {login_data.usuario}")
        except Exception as e:
            print(f"Error al generar token: {str(e)}")
            return {
                "success": False,
                "message": "Error al generar credenciales"
            }
        
        # Contraseña correcta, generar token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": usuario["usuario"],
                "user_id": usuario["ID"],
                "role": usuario["Rol"]
            },
            expires_delta=access_token_expires
        )

        # Debug: imprimir los primeros caracteres del token para verificación
        token_preview = access_token[:15] + "..." if len(access_token) > 15 else access_token
        print(f"Token generado (preview): {token_preview}")
        
        # Login exitoso
        return {
            "success": True,
            "message": "Login exitoso",
            "rol": usuario["Rol"],
            "user_id": usuario["ID"],
            "token": access_token
        }
    
    except Exception as e:
        print(f"ERROR EN LOGIN: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": "Error en el servidor"
        }
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Para proteger rutas específicas, agrega la dependencia get_current_user
# Ejemplo:
@app.get("/procesos/protegido")
def obtener_procesos_protegido(
    establecimiento_id: int = None,
    current_user: TokenData = Depends(get_current_user)
):
    # Verificar permisos basados en el rol si es necesario
    if current_user.role not in ["Admin", "Staff", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para acceder a este recurso")
    
    # Implementa la lógica del endpoint
    return obtener_procesos(establecimiento_id)

# Para proteger rutas específicas, agrega la dependencia get_current_user
# Ejemplo:
@app.get("/procesos/protegido")
def obtener_procesos_protegido(
    establecimiento_id: int = None,
    current_user: TokenData = Depends(get_current_user)
):
    # Verificar permisos basados en el rol si es necesario
    if current_user.role not in ["Admin", "Staff", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para acceder a este recurso")
    
    # Implementa la lógica del endpoint
    return obtener_procesos(establecimiento_id)

@app.get("/procesos")
def obtener_procesos(establecimiento_id: int = None):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar si la tabla procesos2 existe
        cursor.execute("SHOW TABLES LIKE 'procesos2'")
        if not cursor.fetchone():
            print("La tabla procesos2 no existe")
            return {"procesos": []}  # Devolver lista vacía si la tabla no existe
        
        # Si tenemos un ID de establecimiento, filtrar por él
        if establecimiento_id is not None:
            print(f"Obteniendo procesos para establecimiento: {establecimiento_id}")
            cursor.execute("SELECT * FROM procesos2 WHERE establecimiento_id = %s", (establecimiento_id,))
        else:
            # Si no, obtener todos los procesos
            print("Obteniendo todos los procesos")
            cursor.execute("SELECT * FROM procesos2")
        
        procesos = cursor.fetchall()
        
        # Depuración: imprimir procesos encontrados
        print(f"Procesos encontrados: {len(procesos)}")
        for proceso in procesos[:3]:  # Imprimir los primeros 3 para depuración
            print(f"Proceso: {proceso}")
        
        # Convertir las fechas a strings si es necesario
        for proceso in procesos:
            if 'fecha_inicio' in proceso:
                if proceso['fecha_inicio'] is not None and not isinstance(proceso['fecha_inicio'], str):
                    proceso['fecha_inicio'] = proceso['fecha_inicio'].strftime('%Y-%m-%d')
            
            if 'fecha_fin' in proceso:
                if proceso['fecha_fin'] is not None and not isinstance(proceso['fecha_fin'], str):
                    proceso['fecha_fin'] = proceso['fecha_fin'].strftime('%Y-%m-%d')
        
        return {"procesos": procesos}
    
    except Error as e:
        print(f"Error al consultar procesos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

@app.get("/procesos/{id}")
def obtener_proceso_por_id(id: int):
    """
    Obtiene un proceso específico por su ID
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Consulta SQL para obtener el proceso por ID
        cursor.execute("SELECT * FROM procesos2 WHERE id = %s", (id,))
        proceso = cursor.fetchone()
        
        if not proceso:
            raise HTTPException(status_code=404, detail="Proceso no encontrado")
        
        # Depuración: imprimir campos críticos
        print(f"ID: {proceso['id']}")
        print(f"TIPO_PROCESO: {proceso.get('tipo_proceso', 'NO EXISTE ESTE CAMPO')}")
        print(f"DESCRIPCION: {proceso.get('descripcion', 'NO EXISTE ESTE CAMPO')}")
        
        # Convertir fechas a strings de forma segura
        if 'fecha_inicio' in proceso and proceso['fecha_inicio'] is not None:
            if not isinstance(proceso['fecha_inicio'], str):
                proceso['fecha_inicio'] = proceso['fecha_inicio'].strftime('%Y-%m-%d')
        
        if 'fecha_fin' in proceso and proceso['fecha_fin'] is not None:
            if not isinstance(proceso['fecha_fin'], str):
                proceso['fecha_fin'] = proceso['fecha_fin'].strftime('%Y-%m-%d')
        
        return proceso
    
    except Error as e:
        print(f"Error al consultar proceso: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/establecimientos")
def obtener_establecimientos():
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar si la tabla existe (probando con diferentes casos)
        cursor.execute("SHOW TABLES LIKE 'Establecimientos'")
        if not cursor.fetchone():
            # Intentar con minúsculas si no encuentra la tabla
            cursor.execute("SHOW TABLES LIKE 'establecimientos'")
            if not cursor.fetchone():
                print("La tabla de establecimientos no existe")
                return {"establecimientos": []}
            else:
                table_name = "establecimientos"
        else:
            table_name = "Establecimientos"
        
        # Consultar los establecimientos
        cursor.execute(f"SELECT * FROM {table_name}")
        establecimientos = cursor.fetchall()
        
        # Formatear los resultados para garantizar consistencia
        formatted_establecimientos = []
        for establecimiento in establecimientos:
            # Asegurarse de que los campos estén en el formato esperado
            formatted_establecimiento = {
                "id": establecimiento.get('id') or establecimiento.get('ID'),
                "nombre": establecimiento.get('nombre') or establecimiento.get('Nombre'),
                "direccion": establecimiento.get('direccion') or establecimiento.get('Direccion', ''),
                "tipo": establecimiento.get('tipo') or establecimiento.get('Tipo', ''),
                "estado": establecimiento.get('estado') or establecimiento.get('Estado', '')
            }
            formatted_establecimientos.append(formatted_establecimiento)
        
        # Debug - imprimir establecimientos encontrados
        print(f"Establecimientos encontrados: {len(formatted_establecimientos)}")
        
        return {"establecimientos": formatted_establecimientos}
    
    except Error as e:
        print(f"Error detallado al consultar establecimientos: {e}")
        print(f"Tipo de error: {type(e)}")
        
        # Manejar el error de tabla no encontrada
        if "doesn't exist" in str(e) or "no such table" in str(e).lower():
            return {"establecimientos": []}
            
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/usuario_establecimiento")
def obtener_establecimientos_usuario(usuario_id: int = Query(...)):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="Error de conexión")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT e.* FROM establecimientos e
        JOIN usuario_establecimiento ue ON e.id = ue.establecimiento_id
        WHERE ue.usuario_id = %s
        """
        cursor.execute(query, (usuario_id,))
        establecimientos = cursor.fetchall()
        
        # AQUÍ ESTÁ EL CAMBIO - Devolvemos con la clave "establecimientos"
        return {"establecimientos": establecimientos}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.post("/procesos")
def agregar_proceso(proceso: Proceso, request: Request):
    """
    Endpoint para agregar un nuevo proceso.
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor()
        
        # Log para depuración
        print(f"Recibido datos de proceso: {proceso.dict(by_alias=True)}")
        
        # Corregir campo "nombre" por "tipo_proceso"
        query = """
            INSERT INTO procesos2 (tipo_proceso, descripcion, establecimiento_id, fecha_inicio, fecha_fin, 
                               frecuencia, horario, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Valores a insertar
        valores = (
            proceso.tipo_proceso,  # Usar tipo_proceso en lugar de nombre
            proceso.descripcion,
            proceso.establecimiento_id,
            proceso.fecha_inicio,
            proceso.fecha_fin,
            proceso.frecuencia,
            proceso.horario,
            proceso.estado or "No verificado"  # Valor por defecto
        )
        
        # Ejecutar consulta
        cursor.execute(query, valores)
        conexion.commit()
        
        # Obtener el ID del proceso insertado
        proceso_id = cursor.lastrowid
        
        return {"success": True, "message": "Proceso agregado correctamente", "proceso_id": proceso_id}
    
    except Error as e:
        print(f"Error detallado al agregar proceso: {e}")
        return {"success": False, "message": f"Error al agregar proceso: {e}"}
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.post("/procesos-raw")
async def agregar_proceso_raw(request: Request):
    """
    Endpoint para agregar un proceso sin validación previa.
    Acepta cualquier JSON que la app envíe.
    """
    try:
        # Recibir datos sin validación
        datos_json = await request.json()
        
        # Imprimir lo que recibimos para depuración
        print(f"JSON recibido: {datos_json}")
        
        conexion = conectar_db()
        if conexion is None:
            return {"success": False, "message": "No se pudo conectar a la base de datos"}
        
        cursor = None
        try:
            cursor = conexion.cursor()
            
            # Extraer campos directamente del JSON
            tipo_proceso = datos_json.get("tipoProceso", "")
            descripcion = datos_json.get("descripcion", "")
            establecimiento_id = datos_json.get("establecimientoId")
            usuario_id = datos_json.get("usuarioId")
            fecha_inicio = datos_json.get("fechaInicio")
            fecha_fin = datos_json.get("fechaFin")
            frecuencia = datos_json.get("frecuencia")
            horario = datos_json.get("horario")
            estado = datos_json.get("estado", "No verificado")
            
            query = """
                INSERT INTO procesos2 (tipo_proceso, descripcion, establecimiento_id, usuario_id, fecha_inicio, fecha_fin, 
                                   frecuencia, horario, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores = (
                tipo_proceso,
                descripcion,
                establecimiento_id,
                usuario_id,
                fecha_inicio,
                fecha_fin,
                frecuencia,
                horario,
                estado
            )
            
            # Ejecutar consulta
            cursor.execute(query, valores)
            conexion.commit()
            
            # Obtener el ID del proceso insertado
            proceso_id = cursor.lastrowid
            
            return {"success": True, "message": "Proceso agregado correctamente", "proceso_id": proceso_id}
            
        except Error as e:
            print(f"Error detallado al agregar proceso raw: {e}")
            return {"success": False, "message": f"Error al agregar proceso: {e}"}
        
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()
                
    except Exception as e:
        return {"success": False, "message": f"Error en el formato de la solicitud: {e}"}

@app.post("/procesos-adaptado")
async def agregar_proceso_adaptado(request: Request):
    """
    Endpoint que se adapta dinámicamente a la estructura de la tabla procesos2
    """
    try:
        # Recibir datos sin validación
        datos_json = await request.json()
        
        conexion = conectar_db()
        if conexion is None:
            return {"success": False, "message": "No se pudo conectar a la base de datos"}
        
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            
            # Obtener estructura real de la tabla
            cursor.execute("DESCRIBE procesos2")
            columnas = [col["Field"] for col in cursor.fetchall()]
            print(f"Columnas en tabla procesos2: {columnas}")
            
            # Mapeo de campos del JSON a campos de la tabla
            campo_mapping = {
                "tipoProceso": "tipo_proceso",
                "descripcion": "descripcion",
                "establecimientoId": "establecimiento_id",
                "usuarioId": "usuario_id",
                "fechaInicio": "fecha_inicio",
                "fechaFin": "fecha_fin",
                "frecuencia": "frecuencia",
                "horario": "horario",
                "estado": "estado",
                "ubicacion": "ubicacion"
            }
            
            # Construir consulta dinámicamente solo con columnas existentes
            campos = []
            valores = []
            
            for json_campo, db_campo in campo_mapping.items():
                if db_campo in columnas and json_campo in datos_json:
                    campos.append(db_campo)
                    valores.append(datos_json.get(json_campo))
            
            # Construir consulta SQL
            placeholders = ", ".join(["%s"] * len(campos))
            query = f"INSERT INTO procesos2 ({', '.join(campos)}) VALUES ({placeholders})"
            
            print(f"Query dinámica: {query}")
            print(f"Valores: {valores}")
            
            # Ejecutar consulta
            cursor.execute(query, valores)
            conexion.commit()
            
            # Obtener el ID del proceso insertado
            proceso_id = cursor.lastrowid
            
            return {"success": True, "message": "Proceso agregado correctamente", "proceso_id": proceso_id}
            
        except Error as e:
            print(f"Error detallado al agregar proceso adaptado: {e}")
            return {"success": False, "message": f"Error al agregar proceso: {e}"}
        
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()
                
    except Exception as e:
        return {"success": False, "message": f"Error en el formato de la solicitud: {e}"}

@app.delete("/procesos/{id}")
def eliminar_proceso(id: int = Path(..., description="ID del proceso a eliminar")):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor()
        # Consulta SQL para eliminar un proceso por ID
        cursor.execute("DELETE FROM procesos2 WHERE id = %s", (id,))
        
        conexion.commit()
        
        # Verificar si se eliminó algún registro
        if cursor.rowcount > 0:
            return {"success": True, "message": "Proceso eliminado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="No se encontró el proceso especificado")
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar de la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

@app.post("/asignar_establecimiento")
def asignar_establecimiento(usuario_id: int = Query(...), establecimiento_id: int = Query(...)):
    """
    Asigna un establecimiento a un usuario a través de la tabla intermedia
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor()
        
        # Verificar si la asignación ya existe
        cursor.execute(
            "SELECT * FROM usuario_establecimiento WHERE usuario_id = %s AND establecimiento_id = %s", 
            (usuario_id, establecimiento_id)
        )
        
        if cursor.fetchone():
            return {
                "success": False,
                "message": "Este usuario ya tiene asignado este establecimiento"
            }
        
        # Insertar la nueva asignación
        cursor.execute(
            "INSERT INTO usuario_establecimiento (usuario_id, establecimiento_id) VALUES (%s, %s)",
            (usuario_id, establecimiento_id)
        )
        
        conexion.commit()
        
        return {
            "success": True,
            "message": "Establecimiento asignado correctamente al usuario"
        }
    
    except Error as e:
        print(f"Error al asignar establecimiento: {e}")
        return {
            "success": False,
            "message": f"Error al asignar: {str(e)}"
        }
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para obtener comentarios de un proceso
@app.get("/procesos/{proceso_id}/comentarios")
def obtener_comentarios(proceso_id: int = Path(...)):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Primero verificamos si la columna fecha_creacion existe
        cursor.execute("SHOW COLUMNS FROM proceso_comentarios LIKE 'fecha_creacion'")
        tiene_fecha = cursor.fetchone() is not None
        
        # Consulta SQL adaptada según si existe la columna o no
        if tiene_fecha:
            query = """
            SELECT c.id, c.proceso_id, c.usuario_id, c.texto AS comentario, c.fecha_creacion, 
                   u.Nombre as nombre_usuario, u.apellido
            FROM proceso_comentarios c
            JOIN usuarios u ON c.usuario_id = u.ID
            WHERE c.proceso_id = %s
            ORDER BY c.fecha_creacion DESC
            """
        else:
            query = """
            SELECT c.id, c.proceso_id, c.usuario_id, c.texto AS comentario, 
                   u.Nombre as nombre_usuario, u.apellido
            FROM proceso_comentarios c
            JOIN usuarios u ON c.usuario_id = u.ID
            WHERE c.proceso_id = %s
            """
        
        cursor.execute(query, (proceso_id,))
        comentarios = cursor.fetchall()
        
        # Formatear información del usuario y fecha
        for comentario in comentarios:
            comentario['nombre_usuario'] = f"{comentario['nombre_usuario']} {comentario.get('apellido', '')}"
            if 'fecha_creacion' in comentario and not isinstance(comentario['fecha_creacion'], str):
                comentario['fecha_creacion'] = comentario['fecha_creacion'].strftime('%d-%m-%Y %H:%M')
        
        return {"comentarios": comentarios}  # Envolver en un objeto con la clave "comentarios"
    
    except Error as e:
        print(f"Error al consultar comentarios: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para agregar un comentario
@app.post("/procesos/{proceso_id}/comentarios")
def crear_comentario(proceso_id: int, comentario: ProcesoComentario):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        print(f"Creando comentario: proceso_id={proceso_id}, usuario_id={comentario.usuario_id}, texto={comentario.comentario}")
        
        # Insertar comentario
        query = """
        INSERT INTO proceso_comentarios (proceso_id, usuario_id, texto, fecha_creacion)
        VALUES (%s, %s, %s, NOW())
        """
        
        cursor.execute(query, (
            proceso_id,
            comentario.usuario_id,  # Ahora este campo existe en el modelo
            comentario.comentario   # En la DB se almacena como 'texto'
        ))
        
        conexion.commit()
        
        # Obtener el ID del comentario insertado
        nuevo_id = cursor.lastrowid
        
        # Devolver el comentario creado con datos adicionales
        return {
            "id": nuevo_id,
            "proceso_id": proceso_id,
            "usuario_id": comentario.usuario_id,
            "comentario": comentario.comentario,
            "fecha_creacion": datetime.now().strftime('%d-%m-%Y %H:%M')
        }
    
    except Error as e:
        print(f"Error al crear comentario: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para obtener imágenes de un proceso
@app.get("/procesos/{proceso_id}/imagenes")
def obtener_imagenes(proceso_id: int = Path(...)):
    """
    Obtiene todas las imágenes de un proceso
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        query = """
        SELECT i.*, u.Nombre as nombre_usuario, u.apellido
        FROM proceso_imagenes i
        JOIN usuarios u ON i.usuario_id = u.ID
        WHERE i.proceso_id = %s
        """
        
        cursor.execute(query, (proceso_id,))
        imagenes = cursor.fetchall()
        
        # Formatear información
        for imagen in imagenes:
            imagen['nombre_usuario'] = f"{imagen['nombre_usuario']} {imagen.get('apellido', '')}"
            if 'fecha_subida' in imagen and not isinstance(imagen['fecha_subida'], str):
                imagen['fecha_subida'] = imagen['fecha_subida'].strftime('%d-%m-%Y %H:%M')
        
        return imagenes
    
    except Error as e:
        print(f"Error al consultar imágenes: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# Endpoint para subir una imagen
@app.post("/procesos/{proceso_id}/imagenes")
async def subir_imagen(
    proceso_id: int = Path(...),
    usuario_id: int = Form(...),
    imagen: UploadFile = File(...)
):
    try:
        # Verificar si es una imagen válida
        if not imagen.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Crear directorios si no existen
        proceso_dir = os.path.join(UPLOAD_DIR, f"proceso_{proceso_id}")
        if not os.path.exists(proceso_dir):
            os.makedirs(proceso_dir)
        
        # Generar nombre único para la imagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{imagen.filename}"
        filepath = os.path.join(proceso_dir, filename)
        
        print(f"Guardando imagen en: {filepath}")
        
        # Guardar archivo
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        
        # Calcular ruta relativa para almacenar en la base de datos
        ruta_relativa = f"uploads/proceso_{proceso_id}/{filename}"
        
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
        
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            
            # Verificar si la tabla existe y crearla si no
            cursor.execute("SHOW TABLES LIKE 'proceso_imagenes'")
            if not cursor.fetchone():
                # Crear tabla si no existe
                cursor.execute("""
                CREATE TABLE proceso_imagenes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    proceso_id INT NOT NULL,
                    usuario_id INT NOT NULL,
                    ruta_imagen VARCHAR(255) NOT NULL,
                    nombre_imagen VARCHAR(255) NOT NULL,
                    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)
                print("Tabla proceso_imagenes creada")
            
            # Verificar si existe la columna fecha_subida
            cursor.execute("SHOW COLUMNS FROM proceso_imagenes LIKE 'fecha_subida'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE proceso_imagenes ADD COLUMN fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP")
                print("Columna fecha_subida añadida a proceso_imagenes")
            
            # Insertar registro de imagen
            query = """
            INSERT INTO proceso_imagenes (proceso_id, usuario_id, ruta_imagen, nombre_imagen)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query, (proceso_id, usuario_id, ruta_relativa, imagen.filename))
            imagen_id = cursor.lastrowid
            conexion.commit()
            
            # Obtener la imagen recién creada con info del usuario
            query_select = """
            SELECT i.*, u.Nombre as nombre_usuario, u.apellido
            FROM proceso_imagenes i
            JOIN usuarios u ON i.usuario_id = u.ID
            WHERE i.id = %s
            """
            
            cursor.execute(query_select, (imagen_id,))
            nueva_imagen = cursor.fetchone()
            
            # Formatear información
            if nueva_imagen:
                nueva_imagen['nombre_usuario'] = f"{nueva_imagen['nombre_usuario']} {nueva_imagen.get('apellido', '')}"
                if 'fecha_subida' in nueva_imagen and not isinstance(nueva_imagen['fecha_subida'], str):
                    nueva_imagen['fecha_subida'] = nueva_imagen['fecha_subida'].strftime('%d-%m-%Y %H:%M')
            
            return nueva_imagen
        
        except Error as e:
            print(f"Error al guardar imagen: {e}")
            raise HTTPException(status_code=500, detail=f"Error al insertar en la base de datos: {e}")
        
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()
    except Exception as e:
        print(f"Error al guardar imagen: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al guardar imagen: {str(e)}"
        )

# Endpoint para eliminar un comentario (opcional, si quieres permitirlo)
@app.delete("/procesos/comentarios/{comentario_id}")
def eliminar_comentario(comentario_id: int = Path(...)):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM proceso_comentarios WHERE id = %s", (comentario_id,))
        conexion.commit()
        
        if cursor.rowcount > 0:
            return {"success": True, "message": "Comentario eliminado correctamente"}
        else:
            raise HTTPException(status_code=404, detail="No se encontró el comentario")
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar de la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para eliminar una imagen (opcional)
@app.delete("/procesos/imagenes/{imagen_id}")
def eliminar_imagen(imagen_id: int = Path(...)):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        # Primero obtener la ruta de la imagen
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT ruta_imagen FROM proceso_imagenes WHERE id = %s", (imagen_id,))
        imagen = cursor.fetchone()
        
        if not imagen:
            raise HTTPException(status_code=404, detail="No se encontró la imagen")
        
        # Eliminar el archivo físico
        ruta_completa = os.path.join(os.path.dirname(__file__), imagen['ruta_imagen'])
        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)
        
        # Eliminar el registro de la base de datos
        cursor.execute("DELETE FROM proceso_imagenes WHERE id = %s", (imagen_id,))
        conexion.commit()
        
        return {"success": True, "message": "Imagen eliminada correctamente"}
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar de la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.post("/avisos/", response_model=AvisoResponse)
def crear_aviso(aviso: AvisoCreate):
    """
    Crea un nuevo aviso en la base de datos
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)

        # Debug - imprimir datos recibidos
        print(f"Creando aviso con datos: {aviso.dict()}")
        
        # Consulta SQL para insertar el nuevo aviso
        query = """
            INSERT INTO avisos (nombre, categoria, descripcion, establecimiento_id, usuario_id, fecha_creacion, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        # Crear la fecha actual
        fecha_actual = datetime.now()
        fecha_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
        
        # Valores para la consulta (incluyendo estado por defecto)
        valores = (
            aviso.nombre, 
            aviso.categoria, 
            aviso.descripcion, 
            aviso.establecimientoId,
            aviso.usuarioId,
            fecha_str,
            "Pendiente"  # Estado por defecto
        )
        
        # Debug - imprimir query y valores
        print(f"Ejecutando query: {query}")
        print(f"Con valores: {valores}")
        
        # Ejecutar consulta
        cursor.execute(query, valores)
        conexion.commit()
        
        # Obtener el ID generado
        aviso_id = cursor.lastrowid
        print(f"Aviso creado con ID: {aviso_id}")
        
        # Devolver el objeto creado
        return {
            "id": aviso_id,
            "nombre": aviso.nombre,
            "categoria": aviso.categoria,
            "descripcion": aviso.descripcion,
            "establecimientoId": aviso.establecimientoId,
            "usuarioId": aviso.usuarioId,
            "fechaCreacion": fecha_str,
            "estado": "Pendiente"
        }
    
    except Error as e:
        print(f"ERROR al crear aviso: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear el aviso: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.put("/avisos/{aviso_id}")
def actualizar_aviso(aviso_id: int, aviso_update: AvisoUpdate):
    """
    Actualiza un aviso existente, incluyendo su estado
    """
    print(f"Recibiendo solicitud para actualizar aviso {aviso_id} con datos: {aviso_update}")
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar si el aviso existe
        cursor.execute("SELECT * FROM avisos WHERE id = %s", (aviso_id,))
        aviso = cursor.fetchone()
        if not aviso:
            raise HTTPException(status_code=404, detail=f"Aviso con ID {aviso_id} no encontrado")
        
        # Construir consulta dinámica con los campos a actualizar
        campos_actualizados = []
        valores = []
        
        # Use aviso_update (Pydantic model) instead of aviso (dict)
        if aviso_update.nombre is not None:
            campos_actualizados.append("nombre = %s")
            valores.append(aviso_update.nombre)
            
        if aviso_update.categoria is not None:
            campos_actualizados.append("categoria = %s")
            valores.append(aviso_update.categoria)
            
        if aviso_update.descripcion is not None:
            campos_actualizados.append("descripcion = %s")
            valores.append(aviso_update.descripcion)
            
        if aviso_update.establecimientoId is not None:
            campos_actualizados.append("establecimiento_id = %s")
            valores.append(aviso_update.establecimientoId)
            
        if aviso_update.usuarioId is not None:
            campos_actualizados.append("usuario_id = %s")
            valores.append(aviso_update.usuarioId)
        
        # Verificar si el estado es válido
        if aviso_update.estado is not None:
            if aviso_update.estado not in ESTADOS_AVISOS:
                raise HTTPException(status_code=400, detail=f"Estado inválido. Opciones válidas: {', '.join(ESTADOS_AVISOS)}")
            campos_actualizados.append("estado = %s")
            valores.append(aviso_update.estado)
        
        # Si no hay campos para actualizar
        if not campos_actualizados:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        # Agregar el ID al final de los valores para la cláusula WHERE
        valores.append(aviso_id)
        
        # Construir y ejecutar consulta de actualización
        query = f"UPDATE avisos SET {', '.join(campos_actualizados)} WHERE id = %s"
        print(f"Ejecutando query: {query} con valores: {valores}")
        cursor.execute(query, valores)
        conexion.commit()
        
        # Obtener el aviso actualizado
        cursor.execute("""
            SELECT a.*, e.nombre as nombreEstablecimiento, u.Nombre as nombreUsuario 
            FROM avisos a
            LEFT JOIN Establecimientos e ON a.establecimiento_id = e.id
            LEFT JOIN usuarios u ON a.usuario_id = u.ID
            WHERE a.id = %s
        """, (aviso_id,))
        
        aviso_actualizado = cursor.fetchone()
        
        if not aviso_actualizado:
            raise HTTPException(status_code=404, detail="No se pudo recuperar el aviso actualizado")
        
        # Formatear respuesta según el modelo AvisoResponse
        respuesta = {
            "id": aviso_actualizado["id"],
            "nombre": aviso_actualizado["nombre"],
            "descripcion": aviso_actualizado["descripcion"],
            "categoria": aviso_actualizado["categoria"],
            "establecimientoId": aviso_actualizado["establecimiento_id"],
            "usuarioId": aviso_actualizado["usuario_id"],
            "fechaCreacion": aviso_actualizado["fecha_creacion"].strftime('%Y-%m-%d %H:%M:%S') if isinstance(aviso_actualizado["fecha_creacion"], datetime) else aviso_actualizado["fecha_creacion"],
            "estado": aviso_actualizado.get("estado", "Pendiente"),
            "nombreEstablecimiento": aviso_actualizado.get("nombreEstablecimiento", ""),
            "nombreUsuario": aviso_actualizado.get("nombreUsuario", "")
        }
        
        print(f"Aviso actualizado exitosamente: {aviso_id}")
        return respuesta
    
    except Error as e:
        print(f"Error al actualizar aviso: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar el aviso: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/usuarios")
async def obtener_usuarios():
    """Obtiene la lista de todos los usuarios con información de sus establecimientos."""
    try:
        conexion = conectar_db()
        if not conexion:
            return {"success": False, "message": "Error de conexión a la base de datos"}
            
        cursor = conexion.cursor(dictionary=True)
        
        # Realizar JOIN para obtener también el nombre del establecimiento
        query = """
            SELECT u.ID, u.Nombre, u.apellido, u.usuario, u.Rol, 
                   e.id as establecimiento_id, e.nombre as establecimiento_nombre
            FROM usuarios u
            LEFT JOIN usuario_establecimiento ue ON u.ID = ue.usuario_id
            LEFT JOIN establecimientos e ON ue.establecimiento_id = e.id
            ORDER BY u.ID
        """
        
        cursor.execute(query)
        usuarios = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return {"usuarios": usuarios}
        
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return {"success": False, "message": f"Error al obtener usuarios: {str(e)}"}

@app.get("/avisos/")
def obtener_avisos(establecimiento_id: Optional[int] = Query(None)):
    """
    Obtiene todos los avisos de la base de datos.
    Opcionalmente filtra por establecimiento si se proporciona un ID.
    Incluye nombres de establecimiento y usuario en la respuesta.
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar si la tabla avisos existe
        cursor.execute("SHOW TABLES LIKE 'avisos'")
        if not cursor.fetchone():
            print("La tabla avisos no existe")
            return {"avisos": []}  # Devolver lista vacía si la tabla no existe

        # Construir la consulta SQL basada en si hay un ID de establecimiento
        if (establecimiento_id is not None):
            query = """
                SELECT a.*, e.nombre AS nombre_establecimiento, u.Nombre AS nombre_usuario, u.apellido
                FROM avisos a
                LEFT JOIN Establecimientos e ON a.establecimiento_id = e.id
                LEFT JOIN usuarios u ON a.usuario_id = u.ID
                WHERE a.establecimiento_id = %s
                ORDER BY a.fecha_creacion DESC
            """
            cursor.execute(query, (establecimiento_id,))
        else:
            query = """
                SELECT a.*, e.nombre AS nombre_establecimiento, u.Nombre AS nombre_usuario, u.apellido
                FROM avisos a
                LEFT JOIN Establecimientos e ON a.establecimiento_id = e.id
                LEFT JOIN usuarios u ON a.usuario_id = u.ID
                ORDER BY a.fecha_creacion DESC
            """
            cursor.execute(query)
        
        avisos = cursor.fetchall()
        
        # Formatear los datos para la respuesta
        formatted_avisos = []
        for aviso in avisos:
            # Combinar nombre y apellido del usuario
            nombre_completo = f"{aviso.get('nombre_usuario', '')} {aviso.get('apellido', '')}".strip()
            
            # Formatear la fecha
            fecha_creacion = aviso.get('fecha_creacion')
            if fecha_creacion and not isinstance(fecha_creacion, str):
                fecha_creacion = fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            
            # Crear el objeto aviso formateado
            formatted_aviso = {
                "id": aviso.get('id'),
                "nombre": aviso.get('nombre'),
                "descripcion": aviso.get('descripcion'),
                "categoria": aviso.get('categoria'),
                "establecimientoId": aviso.get('establecimiento_id'),
                "usuarioId": aviso.get('usuario_id'),
                "fechaCreacion": fecha_creacion,
                "nombreEstablecimiento": aviso.get('nombre_establecimiento'),
                "nombreUsuario": nombre_completo,
                "estado": aviso.get('estado', 'Pendiente')  # Incluir estado con valor por defecto
            }
            formatted_avisos.append(formatted_aviso)
        
        return {"avisos": formatted_avisos}
    
    except Error as e:
        print(f"Error detallado al consultar avisos: {e}")
        print(f"Tipo de error: {type(e)}")
        
        # Manejar el error de tabla no encontrada
        if "doesn't exist" in str(e) or "no such table" in str(e).lower():
            return {"avisos": []}
            
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/verificar_token")
def verificar_token_endpoint(current_user: TokenData = Depends(get_current_user)):
    """
    Endpoint para verificar si un token es válido
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.user_id,
            "username": current_user.username,
            "role": current_user.role
        }
    }

@app.post("/debug/headers")
async def debug_headers(request: Request):
    """Endpoint para depurar los headers de la petición."""
    headers = dict(request.headers)
    auth_header = headers.get("authorization")
    
    # Verificar si el token está presente y es válido
    token_valid = False
    token_payload = None
    if (auth_header and auth_header.startswith("Bearer ")):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_valid = True
            token_payload = payload
        except Exception as e:
            token_payload = {"error": str(e)}
    
    return {
        "headers": headers,
        "auth_present": auth_header is not None,
        "token_valid": token_valid,
        "token_payload": token_payload
    }

@app.get("/debug/token-info")
def debug_token_info(token: str = Query(..., description="Token JWT para analizar")):
    """Endpoint para analizar un token JWT"""
    try:
        # Decodificar sin verificar firma (para diagnóstico)
        payload = jwt.decode(token, options={"verify_signature": False}, algorithms=[ALGORITHM])
        return {
            "is_valid_format": True,
            "payload": payload,
            "expiry": datetime.fromtimestamp(payload.get("exp", 0))
        }
    except JWTError as e:
        return {
            "is_valid_format": False,
            "error": str(e)
        }

@app.post("/debug/procesos-request")
async def debug_procesos_request(request: Request):
    """Endpoint para depurar las peticiones a /procesos"""
    body = await request.body()
    headers = {k: v for k, v in request.headers.items()}
    
    # Intentar analizar el cuerpo JSON
    try:
        json_body = await request.json()
    except:
        json_body = "No es un JSON válido"
    
    return {
        "headers": headers,
        "auth_header": request.headers.get("Authorization"),
        "raw_body": body.decode("utf-8", errors="ignore"),
        "json_body": json_body,
        "method": request.method,
        "url": str(request.url)
    }

@app.post("/debug/proceso-model")
async def debug_proceso_model(request: Request):
    """Endpoint para verificar el formato exacto que envía la app"""
    try:
        body = await request.body()
        # Intentar decodificar el JSON
        json_str = body.decode('utf-8')
        import json
        data = json.loads(json_str)
        
        return {
            "received_json": data,
            "content_type": request.headers.get("Content-Type"),
            "headers": {k: v for k, v in request.headers.items()}
        }
    except Exception as e:
        return {"error": str(e), "raw_body": str(body)}

@app.post("/debug/proceso-completo")
async def debug_proceso_completo(request: Request):
    """Endpoint detallado para ver exactamente qué envía la app Android"""
    try:
        # Obtener y decodificar el cuerpo de la petición
        body = await request.body()
        json_str = body.decode('utf-8')
        
        import json
        data = json.loads(json_str)
        
        # Analizar la estructura de la tabla
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("DESCRIBE procesos2")
        table_structure = cursor.fetchall()
        
        # Verificar qué campos están presentes/ausentes
        required_fields = ["tipo_proceso", "descripcion", "establecimiento_id"]
        missing_fields = [field for field in required_fields if field not in data]
        
        # Preparar respuesta de diagnóstico
        return {
            "received_data": data,
            "table_structure": table_structure,
            "missing_fields": missing_fields,
            "content_type": request.headers.get("Content-Type"),
            "headers": {k: v for k, v in request.headers.items()}
        }
    except Exception as e:
        return {"error": str(e), "raw_body": str(body) if 'body' in locals() else "No body found"}

@app.delete("/avisos/{aviso_id}")
def eliminar_aviso(aviso_id: int = Path(..., description="ID del aviso a eliminar")):
    """
    Elimina un aviso de la base de datos por su ID
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor()
        
        # Verificar que el aviso existe
        cursor.execute("SELECT * FROM avisos WHERE id = %s", (aviso_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Aviso no encontrado")
        
        # Eliminar el aviso
        cursor.execute("DELETE FROM avisos WHERE id = %s", (aviso_id,))
        conexion.commit()
        
        # Verificar si se eliminó algún registro
        if cursor.rowcount > 0:
            return {"success": True, "message": "Aviso eliminado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="No se pudo eliminar el aviso")
    
    except Error as e:
        print(f"Error al eliminar aviso: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar de la base de datos: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/debug/auth-test")
async def debug_auth_test(request: Request):
    """Endpoint para probar problemas de autenticación"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return {
            "status": "error",
            "message": "No Authorization header provided",
            "all_headers": {k: v for k, v in request.headers.items()}
        }
        
    if not auth_header.startswith("Bearer "):
        return {
            "status": "error", 
            "message": "Authorization header does not contain Bearer token",
            "auth_header": auth_header
        }
        
    token = auth_header.split(" ")[1]
    
    try:
        # Intentar decodificar sin verificar firma
        unverified_payload = jwt.decode(token, options={"verify_signature": False}, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(unverified_payload.get("exp", 0))
        
        # Luego con verificación completa
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return {
                "status": "success",
                "token_valid": True,
                "payload": payload,
                "expiration": exp_time.strftime("%Y-%m-%d %H:%M:%S"),
                "current_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "secret_key_first_chars": SECRET_KEY[:5] + "..."
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": "Token signature invalid",
                "error": str(e),
                "unverified_payload": unverified_payload,
                "expiration": exp_time.strftime("%Y-%m-%d %H:%M:%S"),
                "secret_key_first_chars": SECRET_KEY[:5] + "..."
            }
    except Exception as e:
        return {
            "status": "error",
            "reason": "Token format invalid",
            "error": str(e)
        }

@app.get("/debug/check-token")
async def debug_check_token(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return {
            "valid": False,
            "message": "No se encontró el encabezado Authorization",
            "headers_received": dict(request.headers)
        }
    
    if not auth_header.startswith("Bearer "):
        return {
            "valid": False,
            "message": "El formato del encabezado es incorrecto",
            "header_found": auth_header
        }
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valid": True,
            "username": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "role": payload.get("role"),
            "expires": datetime.fromtimestamp(payload.get("exp")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Token inválido: {str(e)}"
        }

@app.get("/debug/token")
async def debug_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return {"valid": False, "message": "No se encontró el encabezado Authorization"}

    if not auth_header.startswith("Bearer "):
        return {"valid": False, "message": "El formato del encabezado es incorrecto"}

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valid": True,
            "payload": payload,
            "expires": datetime.fromtimestamp(payload.get("exp")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"valid": False, "message": f"Token inválido: {str(e)}"}

# Primero, definir el modelo para la solicitud de creación de usuario
class UsuarioCreate(BaseModel):
    usuario: str
    contraseña: str
    nombre: str
    apellido: str
    rol: str
    establecimiento_id: Optional[int] = None

# First endpoint - requires authentication (for admins to create users)
@app.post("/usuarios/", response_model=dict)
def crear_usuario(usuario: UsuarioCreate, current_user: TokenData = Depends(get_current_user)):
    # Verificar que el usuario tenga permisos de administrador
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="No tiene permisos para realizar esta acción")

    # Lógica para crear el usuario
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Insertar el usuario
        query = """
            INSERT INTO usuarios (Nombre, apellido, usuario, contraseña, Rol)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        valores = (
            usuario.nombre,
            usuario.apellido,
            usuario.usuario,
            usuario.contraseña,
            usuario.rol
        )
        
        cursor.execute(query, valores)
        conexion.commit()

        usuario_id = cursor.lastrowid
        
        # Si se proporcionó un establecimiento_id, asignar al usuario a ese establecimiento
        if usuario.establecimiento_id:
            # Verificar que el establecimiento existe
            cursor.execute("SELECT * FROM Establecimientos WHERE id = %s", (usuario.establecimiento_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, 
                                   detail=f"No existe establecimiento con ID {usuario.establecimiento_id}")
            
            # Asignar el establecimiento al usuario
            query_asignacion = """
                INSERT INTO usuario_establecimiento (usuario_id, establecimiento_id)
                VALUES (%s, %s)
            """
            cursor.execute(query_asignacion, (usuario_id, usuario.establecimiento_id))
            conexion.commit()
            print(f"Usuario {usuario_id} asignado al establecimiento {usuario.establecimiento_id}")
        
        return {
            "success": True,
            "message": "Usuario creado exitosamente",
            "usuario_id": usuario_id,
            "establecimiento_asignado": usuario.establecimiento_id is not None
        }
        
    except Error as e:
        print(f"Error al crear usuario: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear el usuario: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
            

@app.post("/registro")
async def crear_usuario(usuario_data: dict = Body(...)):
    """
    Endpoint para crear usuarios y asignarles establecimientos
    """
    try:
        # Obtener conexión a la base de datos
        conexion = conectar_db()
        if not conexion:
            return {"success": False, "message": "Error de conexión a la base de datos"}
        
        cursor = conexion.cursor()
        
        # 1. Validar campos requeridos
        campos_requeridos = ["nombre", "apellido", "usuario", "contraseña", "rol"]
        for campo in campos_requeridos:
            if campo not in usuario_data or not usuario_data[campo]:
                return {"success": False, "message": f"El campo {campo} es requerido"}
        
        # 2. Validar que el rol sea válido
        roles_permitidos = ['Admin', 'Area Manager', 'Store Manager', 'RRHH', 'Staff']
        if usuario_data["rol"] not in roles_permitidos:
            return {"success": False, "message": f"Rol no válido. Debe ser uno de: {', '.join(roles_permitidos)}"}
        
        # 3. Verificar si el nombre de usuario ya existe
        cursor.execute("SELECT ID FROM usuarios WHERE usuario = %s", (usuario_data["usuario"],))
        if cursor.fetchone():
            return {"success": False, "message": "Este nombre de usuario ya está en uso"}
        
        # 4. Generar hash de la contraseña
        hashed_password = pwd_context.hash(usuario_data["contraseña"])
        
        # 5. Insertar el nuevo usuario
        query_usuario = """
            INSERT INTO usuarios (Nombre, apellido, usuario, Contraseña, Rol)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        valores_usuario = (
            usuario_data["nombre"],
            usuario_data["apellido"],
            usuario_data["usuario"],
            hashed_password,
            usuario_data["rol"]
        )
        
        cursor.execute(query_usuario, valores_usuario)
        usuario_id = cursor.lastrowid
        
        # 6. Asignar establecimientos al usuario
        if "establecimientos" in usuario_data and isinstance(usuario_data["establecimientos"], list) and usuario_data["establecimientos"]:
            # Verificar que todos los establecimientos existan
            placeholders = ', '.join(['%s'] * len(usuario_data["establecimientos"]))
            query_check = f"SELECT id FROM establecimientos WHERE id IN ({placeholders})"
            cursor.execute(query_check, usuario_data["establecimientos"])
            establecimientos_existentes = [row[0] for row in cursor.fetchall()]
            
            # Insertar solo los establecimientos que existen
            for est_id in establecimientos_existentes:
                query_relacion = """
                    INSERT INTO usuario_establecimiento (usuario_id, establecimiento_id)
                    VALUES (%s, %s)
                """
                cursor.execute(query_relacion, (usuario_id, est_id))
        
        # Confirmar cambios
        conexion.commit()
        
        return {
            "success": True,
            "message": "Usuario creado correctamente",
            "user_id": usuario_id
        }
        
    except Exception as e:
        # En caso de error, revertir cambios
        if conexion:
            conexion.rollback()
        
        print(f"Error al crear usuario: {str(e)}")
        return {
            "success": False,
            "message": f"Error al crear usuario: {str(e)}"
        }
    
    finally:
        # Cerrar cursor y conexión
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexion' in locals() and conexion and conexion.is_connected():
            conexion.close()

@app.post("/debug/login")
async def debug_login(request: Request):
    body = await request.json()
    return {
        "received_body": body,
        "headers": dict(request.headers)
    }

# Endpoint temporal para regenerar la contraseña de AdminSMOOY
@app.get("/regenerar_contrasena_admin")
def regenerar_contrasena_admin():
    """
    Endpoint temporal para regenerar la contraseña del usuario AdminSMOOY.
    Este endpoint debe eliminarse después de usarlo una vez.
    """
    # Regenerar la contraseña para el usuario AdminSMOOY
    # Usar la misma configuración que en la aplicación
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Generar un nuevo hash para la contraseña "SMOOY"
    hashed_password = pwd_context.hash("SMOOY")

    # Actualizar en la base de datos
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuarios SET Contraseña = %s WHERE usuario = %s", 
                 (hashed_password, "AdminSMOOY"))
    conexion.commit()
    cursor.close()
    conexion.close()

    return {"mensaje": f"Nueva contraseña hash generada para AdminSMOOY: {hashed_password}"}

@app.get("/verify-token")
async def verify_token_endpoint(request: Request):
    """Endpoint para verificar el token"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return {"valid": False, "message": "No Authorization header"}
    
    if not auth_header.startswith("Bearer "):
        return {"valid": False, "message": "Invalid format"}
    
    token = auth_header.split(" ")[1]
    
    try:
        # Intenta decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valid": True,
            "user_info": {
                "username": payload.get("sub"),
                "user_id": payload.get("user_id"),
                "role": payload.get("role")
            },
            "expires": datetime.fromtimestamp(payload.get("exp")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}

# 5. Añade este endpoint para comprobar tokens de manera explícita
@app.get("/verify-token", include_in_schema=False)
async def verify_token_endpoint(request: Request):
    """Endpoint para verificar tokens JWT explícitamente"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return {"valid": False, "error": "No se proporcionó header de autorización"}
        
    if not auth_header.startswith("Bearer "):
        return {"valid": False, "error": "Formato de token incorrecto"}
        
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valid": True,
            "payload": {
                "username": payload.get("sub"),
                "user_id": payload.get("user_id"),
                "role": payload.get("role"),
                "exp": payload.get("exp")
            }
        }
    except JWTError as e:
        return {"valid": False, "error": str(e)}

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

# Lista de rutas públicas que no requieren autenticación
PUBLIC_PATHS = [
    "/login",
    "/registro",
    "/debug/headers",
    "/verify-token",
    "/regenerar_contrasena_admin"  # Eliminar en producción
]

# Función para verificar y decodificar el token JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("user_id")
        role = payload.get("role")
        
        if username is None or user_id is None:
            raise credentials_exception
        
        return {"username": username, "user_id": user_id, "role": role}
    except JWTError:
        raise credentials_exception

# Middleware para verificar JWT en rutas protegidas
@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    path = request.url.path
    
    # Si es una ruta pública, permitir acceso sin verificar token
    if path in PUBLIC_PATHS or path.startswith("/static/"):
        return await call_next(request)
        
    # Para las rutas protegidas, verificar el token
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "No se proporcionó un token válido"}
        )
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Almacenar información del usuario en el request para uso posterior
        request.state.user = {
            "username": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "role": payload.get("role")
        }
    except JWTError as e:
        return JSONResponse(
            status_code=401,
            content={"detail": f"Token inválido o expirado: {str(e)}"}
        )
    
    # Continuar con la solicitud
    return await call_next(request)

# Configuración bcrypt correcta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función auxiliar para crear passwords encriptadas
def get_password_hash(password):
    return pwd_context.hash(password)

# Función auxiliar para verificar passwords
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Endpoint para regenerar contraseñas correctamente
@app.post("/admin/reset-password")
async def admin_reset_password(user_id: int, new_password: str, user: dict = Depends(get_current_user)):
    # Verificar que el usuario actual es administrador
    if user.get("role") != "Administrador":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta operación")
        
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor()
        
        # Generar hash de la nueva contraseña
        hashed_password = get_password_hash(new_password)
        
        # Actualizar contraseña en la base de datos
        cursor.execute("UPDATE usuarios SET Contraseña = %s WHERE ID = %s", 
                     (hashed_password, user_id))
        
        conexion.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        return {"success": True, "message": "Contraseña actualizada correctamente"}
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# Borra TODOS los middleware existentes y usa solo esta implementación

# Lista definitiva de rutas públicas
PUBLIC_PATHS = [
    "/login",
    "/registro",
    "/docs", 
    "/openapi.json",
    "/redoc",
    "/static",
    "/debug/headers",
    "/verify-token",
    "/regenerar_contrasena_admin",
    "/api-status"  # Añadir endpoint de estado
]

@app.middleware("http")
async def verify_jwt_token(request: Request, call_next):
    path = request.url.path
    
    # Verificar si es una ruta pública o empieza con un patrón público
    if path in PUBLIC_PATHS or any(path.startswith(prefix) for prefix in ["/static/", "/docs/", "/openapi.json"]):
        print(f"Acceso permitido a ruta pública: {path}")
        return await call_next(request)
    
        print(f"Error validando token para {path}: {str(e)}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Token inválido o expirado"}
        )
    
    return await call_next(request)

# Importaciones necesarias (verifica que estén al principio del archivo)
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# Configuración de JWT
SECRET_KEY = "tu_clave_secreta_compleja_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

# Configuración de bcrypt para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para verificar contraseñas
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para generar hash de contraseñas
def get_password_hash(password):
    return pwd_context.hash(password)

# Función para crear token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Middleware de verificación JWT
@app.middleware("http")
async def verify_jwt_token(request: Request, call_next):
    # Definir rutas públicas que no requieren autenticación
    public_paths = ["/login", "/registro", "/docs", "/openapi.json", "/redoc", "/static"]
    
    # Si es una ruta pública, permitir acceso sin verificar
    path = request.url.path
    if path in public_paths or any(path.startswith(prefix) for prefix in ["/static/", "/docs/"]):
        return await call_next(request)
    
    # Para las rutas protegidas, verificar el token JWT
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        print(f"🔒 Acceso denegado a {path}: No token proporcionado o formato incorrecto")
        return JSONResponse(
            status_code=401,
            content={"detail": "No se proporcionó un token válido"}
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # Decodificar y verificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Guardar información del usuario en el estado de la solicitud
        request.state.user = {
            "username": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "role": payload.get("role")
        }
        
        # print(f"✅ Token válido para {payload.get('sub')} accediendo a {path}")
    except JWTError as e:
        print(f"❌ Token inválido: {str(e)}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Token inválido o expirado"}
        )
    
    # Continuar con la solicitud
    return await call_next(request)

# Endpoint para login (versión corregida)
@app.post("/login")
def login(login_request: LoginRequest):
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Buscar usuario en la base de datos
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (login_request.usuario,))
        usuario = cursor.fetchone()
        
        if not usuario:
            print(f"❌ Usuario no encontrado: {login_request.usuario}")
            return {
                "success": False,
                "message": "Usuario o contraseña incorrectos"
            }
        
        # Verificar contraseña
        is_password_correct = verify_password(login_request.contraseña, usuario["Contraseña"])
        print(f"Verificación de contraseña para {login_request.usuario}: {is_password_correct}")
        
        if not is_password_correct:
            return {
                "success": False,
                "message": "Usuario o contraseña incorrectos"
            }
        
        # Generar token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": usuario["usuario"],
                "user_id": usuario["ID"],
                "role": usuario["Rol"]
            },
            expires_delta=access_token_expires
        )
        
        print(f"✅ Login exitoso para {usuario['usuario']}, token JWT generado")
        
        # Debug: imprimir los primeros caracteres del token para verificación
        token_preview = access_token[:15] + "..." if len(access_token) > 15 else access_token
        print(f"Token generado (preview): {token_preview}")
        
        return {
            "success": True,
            "message": "Login exitoso",
            "rol": usuario["Rol"],
            "user_id": usuario["ID"],
            "token": access_token
        }
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        return {
            "success": False,
            "message": "Error al procesar la solicitud"
        }
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para regenerar contraseñas con hash bcrypt
@app.post("/admin/reset-password")
async def admin_reset_password(username: str, new_password: str, request: Request):
    # Verificar que el usuario actual es administrador
    if request.state.user.get("role") != "Administrador":
        raise HTTPException(status_code=403, detail="No tiene permisos para esta operación")
        
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor()
        
        # Generar hash de la contraseña
        hashed_password = get_password_hash(new_password)
        
        # Actualizar contraseña en la base de datos
        cursor.execute("UPDATE usuarios SET Contraseña = %s WHERE usuario = %s", 
                     (hashed_password, username))
        
        conexion.commit()
        
        if cursor.rowcount == 0:
            return {"success": False, "message": "Usuario no encontrado"}
            
        return {"success": True, "message": f"Contraseña actualizada para {username}"}
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# migrate_passwords.py
from passlib.context import CryptContext
import mysql.connector
from mysql.connector import Error

# Configuración de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para generar hash de contraseñas
def get_password_hash(password):
    return pwd_context.hash(password)

def conectar_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='smooydb',  # Nombre correcto según archivo SQL
            user='root',         # Usuario por defecto en XAMPP/WAMP
            password='',         # Contraseña vacía por defecto
            port=3306
        )
        if connection.is_connected():
            print("Conexión a MySQL establecida correctamente")
            return connection
    except Error as e:
        print(f"Error al conectarse a MySQL: {e}")
        return None

@app.post("/admin/encriptar_contrasenas")
def encriptar_contrasenas_admin(password: str = Body(...)):
    """Endpoint administrativo para encriptar todas las contraseñas"""
    if password != "clave_admin_secreta":
        raise HTTPException(status_code=403, detail="No autorizado")
        
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="Error de conexión")
    
    # Resto del código de encriptación...

# Endpoints para imágenes de avisos
@app.get("/avisos/{aviso_id}/imagenes")
def obtener_imagenes_aviso(aviso_id: int = Path(...)):
    """
    Obtiene todas las imágenes de un aviso
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT ai.*, u.Nombre as nombre_usuario 
        FROM aviso_imagenes ai
        JOIN usuarios u ON ai.usuario_id = u.ID
        WHERE ai.aviso_id = %s
        """
        cursor.execute(query, (aviso_id,))
        imagenes = cursor.fetchall()
        
        return imagenes
    
    except Error as e:
        print(f"Error al consultar imágenes: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.post("/avisos/{aviso_id}/imagenes")
async def subir_imagen_aviso(
    aviso_id: int = Path(...),
    usuario_id: int = Form(...),
    imagen: UploadFile = File(...)
):
    """
    Sube una imagen asociada a un aviso
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = None
    try:
        # Guardar la imagen en el servidor
        contenido = await imagen.read()
        nombre_archivo = f"aviso_{aviso_id}_{int(time.time())}_{imagen.filename}"
        ruta_relativa = f"uploads/avisos/{nombre_archivo}"
        ruta_completa = os.path.join(UPLOAD_DIR, "avisos", nombre_archivo)
        
        # Asegurarse de que el directorio exista
        os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
        
        with open(ruta_completa, "wb") as f:
            f.write(contenido)
        
        # Registrar en la base de datos
        cursor = conexion.cursor()
        query = """
        INSERT INTO aviso_imagenes (aviso_id, usuario_id, ruta_imagen, nombre_imagen, fecha_subida)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (aviso_id, usuario_id, ruta_relativa, imagen.filename))
        conexion.commit()
        
        imagen_id = cursor.lastrowid
        
        return {
            "id": imagen_id,
            "aviso_id": aviso_id,
            "usuario_id": usuario_id,
            "ruta_imagen": ruta_relativa,
            "nombre_imagen": imagen.filename,
            "fecha_subida": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Error as e:
        print(f"Error al subir imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar en base de datos: {e}")
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.post("/usuarios")
async def crear_usuario(usuario_data: dict):
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        # Validar campos requeridos
        campos_requeridos = ["nombre", "apellido", "usuario", "contraseña", "rol"]
        for campo in campos_requeridos:
            if campo not in usuario_data:
                return {"success": False, "message": f"El campo {campo} es requerido"}
        
        # Verificar si el nombre de usuario ya existe
        cursor.execute("SELECT ID FROM usuarios WHERE usuario = %s", (usuario_data["usuario"],))
        if cursor.fetchone():
            return {"success": False, "message": "Este nombre de usuario ya está en uso"}
        
        # Validar el rol
        roles_validos = ["Admin", "Staff", "Usuario", "Area Manager"]
        if (usuario_data["rol"] not in roles_validos):
            return {"success": False, "message": f"Rol inválido. Debe ser uno de: {', '.join(roles_validos)}"}
        
        # Hash de la contraseña
        hashed_password = pwd_context.hash(usuario_data["contraseña"])
        
        # Insertar el nuevo usuario
        query = """
            INSERT INTO usuarios (Nombre, apellido, usuario, contraseña, Rol)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        valores = (
            usuario_data["nombre"],
            usuario_data["apellido"],
            usuario_data["usuario"],
            hashed_password,
            usuario_data["rol"]
        )
        
        cursor.execute(query, valores)
        usuario_id = cursor.lastrowid
        
        # Manejar la asignación de establecimientos
        if "establecimientos" in usuario_data and isinstance(usuario_data["establecimientos"], list):
            for establecimiento_id in usuario_data["establecimientos"]:
                # Verificar que el establecimiento existe
                cursor.execute("SELECT id FROM Establecimientos WHERE id = %s", (establecimiento_id,))
                if cursor.fetchone():
                    # Crear relación usuario-establecimiento
                    cursor.execute(
                        "INSERT INTO usuario_establecimiento (usuario_id, establecimiento_id) VALUES (%s, %s)",
                        (usuario_id, establecimiento_id)
                    )
                else:
                    print(f"Advertencia: El establecimiento con ID {establecimiento_id} no existe")
        
        conexion.commit()
        
        return {
            "success": True,
            "message": "Usuario creado con éxito",
            "usuario_id": usuario_id
        }
        
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        return {"success": False, "message": f"Error al crear usuario: {str(e)}"}
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/usuarios")
async def obtener_usuarios():
    """Obtiene la lista de todos los usuarios con sus establecimientos agrupados."""
    try:
        conexion = conectar_db()
        if not conexion:
            return {"usuarios": []}
            
        cursor = conexion.cursor(dictionary=True)
        
        # 1. Primero obtenemos la lista de usuarios única
        cursor.execute("SELECT ID, Nombre, apellido, usuario, Rol FROM usuarios ORDER BY ID")
        usuarios_raw = cursor.fetchall()
        
        # 2. Para cada usuario, buscamos sus establecimientos
        usuarios_agrupados = []
        for usuario in usuarios_raw:
            usuario_id = usuario['ID']
            
            # Obtener establecimientos de este usuario
            cursor.execute("""
                SELECT e.id, e.nombre 
                FROM establecimientos e
                JOIN usuario_establecimiento ue ON e.id = ue.establecimiento_id
                WHERE ue.usuario_id = %s
            """, (usuario_id,))
            establecimientos = cursor.fetchall()
            
            # Añadir establecimientos al usuario
            usuario_completo = usuario.copy()
            usuario_completo['establecimientos'] = establecimientos
            
            # También mantener campos individuales para compatibilidad
            if establecimientos:
                usuario_completo['establecimiento_id'] = establecimientos[0]['id']
                usuario_completo['establecimiento_nombre'] = establecimientos[0]['nombre']
            else:
                usuario_completo['establecimiento_id'] = None
                usuario_completo['establecimiento_nombre'] = None
            
            usuarios_agrupados.append(usuario_completo)
        
        cursor.close()
        conexion.close()
        
        return {"usuarios": usuarios_agrupados}
    except Exception as e:
        print(f"Error: {e}")
        return {"usuarios": []}
    
@app.delete("/usuarios/{usuario_id}")
async def eliminar_usuario(usuario_id: int):
    """Elimina un usuario por su ID."""
    try:
        conexion = conectar_db()
        if not conexion:
            return {"success": False, "message": "Error de conexión a la base de datos"}
            
        cursor = conexion.cursor(dictionary=True)
        
        # Paso 1: Verificar si el usuario existe realmente
        cursor.execute("SELECT ID, usuario, Rol FROM usuarios WHERE ID = %s", (usuario_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            # El usuario no existe - proporcionar información clara sobre el error
            print(f"Error al eliminar: Usuario con ID {usuario_id} no encontrado")
            return {"success": False, "message": f"Usuario con ID {usuario_id} no encontrado en la base de datos"}
        
        # Log para depuración
        print(f"Encontrado usuario a eliminar: {usuario}")
        
        # Paso 2: Verificar relaciones con otras tablas
        cursor.execute("SELECT COUNT(*) as count FROM usuario_establecimiento WHERE usuario_id = %s", (usuario_id,))
        rel_count = cursor.fetchone()['count']
        print(f"Este usuario tiene {rel_count} relaciones en usuario_establecimiento")
        
        # Paso 3: Eliminar primero las relaciones en tablas dependientes
        cursor.execute("DELETE FROM usuario_establecimiento WHERE usuario_id = %s", (usuario_id,))
        rel_deleted = cursor.rowcount
        print(f"Eliminadas {rel_deleted} relaciones para el usuario {usuario_id}")
        
        # Paso 4: Luego eliminar el usuario
        cursor.execute("DELETE FROM usuarios WHERE ID = %s", (usuario_id,))
        user_deleted = cursor.rowcount
        print(f"Eliminados {user_deleted} registros de usuario")
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        if user_deleted > 0:
            return {
                "success": True, 
                "message": f"Usuario '{usuario.get('usuario', 'desconocido')}' (ID: {usuario_id}) eliminado correctamente",
                "details": {
                    "user_id": usuario_id,
                    "relations_removed": rel_deleted
                }
            }
        else:
            return {"success": False, "message": f"No se pudo eliminar el usuario con ID {usuario_id}"}
            
    except Exception as e:
        print(f"Error detallado al eliminar usuario {usuario_id}: {str(e)}")
        return {"success": False, "message": f"Error al eliminar usuario: {str(e)}"}
# Funciones para generación automática de procesos usando la tabla procesos2

# Modelo para las tareas
class TareaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    orden: Optional[int] = 0
    estado: Optional[str] = "Pendiente"

class TareaCreate(TareaBase):
    proceso_id: int

class Tarea(TareaBase):
    id: int
    proceso_id: int
    fecha_creacion: Optional[datetime] = None
    fecha_completado: Optional[datetime] = None
    usuario_completado_id: Optional[int] = None

class TareasResponse(BaseModel):
    tareas: List[Tarea]

@app.get("/procesos/{proceso_id}/tareas", response_model=List[Dict[str, Any]])
async def obtener_tareas_proceso(proceso_id: int = Path(...)):
    """
    Obtiene todas las tareas asociadas a un proceso específico
    """
    try:
        conexion = conectar_db()
        if not conexion:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT t.*, u.Nombre as nombre_usuario_completado, u.usuario as usuario_completado 
            FROM proceso_tareas t
            LEFT JOIN usuarios u ON t.usuario_completado_id = u.ID
            WHERE t.proceso_id = %s
            ORDER BY t.orden, t.id
        """
        
        cursor.execute(query, (proceso_id,))
        tareas = cursor.fetchall()
        
        # Verificar si el proceso existe
        if not tareas and not proceso_existe(conexion, proceso_id):
            raise HTTPException(status_code=404, detail=f"Proceso con ID {proceso_id} no encontrado")
            
        cursor.close()
        conexion.close()
        
        return tareas
        
    except Exception as e:
        print(f"Error al obtener tareas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener tareas: {str(e)}")

@app.post("/establecimientos", response_model=Dict[str, Any])
async def crear_establecimiento(establecimiento_data: Dict[str, Any] = Body(...)):
    """
    Crea un nuevo establecimiento
    """
    try:
        conexion = conectar_db()
        if not conexion:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Verificar campos obligatorios
        if 'nombre' not in establecimiento_data or not establecimiento_data['nombre'].strip():
            raise HTTPException(status_code=400, detail="El nombre del establecimiento es obligatorio")
        
        # Preparar datos para inserción
        nombre = establecimiento_data.get("nombre")
        direccion = establecimiento_data.get("direccion", "")
        tipo = establecimiento_data.get("tipo", "")
        estado = establecimiento_data.get("estado", "activo")
        
        query = """
            INSERT INTO Establecimientos (nombre, direccion, tipo, estado)
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(query, (nombre, direccion, tipo, estado))
        establecimiento_id = cursor.lastrowid
        
        conexion.commit()
        
        return {
            "success": True,
            "message": "Establecimiento creado correctamente",
            "establecimiento_id": establecimiento_id,
            "establecimiento": {
                "id": establecimiento_id,
                "nombre": nombre,
                "direccion": direccion,
                "tipo": tipo,
                "estado": estado
            }
        }
        
    except Exception as e:
        print(f"Error al crear establecimiento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear establecimiento: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/tareas/{id}", response_model=Dict[str, Any])
async def obtener_tarea_por_id(id: int = Path(...), current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene los detalles de una tarea específica por su ID
    """
    conn = conectar_db()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Consultar la tarea con el ID proporcionado
        query = """
            SELECT pt.*, u.Nombre as nombre_usuario_completado
            FROM proceso_tareas pt
            LEFT JOIN usuarios u ON pt.usuario_completado_id = u.ID
            WHERE pt.id = %s
        """
        cursor.execute(query, (id,))
        tarea = cursor.fetchone()
        
        if not tarea:
            raise HTTPException(status_code=404, detail=f"Tarea con ID {id} no encontrada")
        
        return {"id": tarea["id"], 
                "proceso_id": tarea["proceso_id"], 
                "nombre": tarea["nombre"], 
                "descripcion": tarea["descripcion"],
                "orden": tarea["orden"], 
                "estado": tarea["estado"],
                "fecha_creacion": tarea["fecha_creacion"].isoformat() if tarea["fecha_creacion"] else None,
                "fecha_completado": tarea["fecha_completado"].isoformat() if tarea["fecha_completado"] else None,
                "usuario_completado_id": tarea["usuario_completado_id"],
                "nombre_usuario_completado": tarea["nombre_usuario_completado"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tarea: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.post("/procesos/{proceso_id}/tareas", response_model=Dict[str, Any])
async def agregar_tarea_proceso(
    proceso_id: int = Path(...),
    tarea_datos: Dict[str, Any] = Body(...)
):
    """
    Añade una nueva tarea a un proceso específico
    """
    try:
        conexion = conectar_db()
        if not conexion:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Verificar que el proceso existe
        if not proceso_existe(conexion, proceso_id):
            raise HTTPException(status_code=404, detail=f"Proceso con ID {proceso_id} no encontrado")
        
        # Campos obligatorios
        if 'nombre' not in tarea_datos or not tarea_datos['nombre'].strip():
            raise HTTPException(status_code=400, detail="El nombre de la tarea es obligatorio")
        
        # Establecer valores predeterminados
        descripcion = tarea_datos.get("descripcion", "")
        orden = tarea_datos.get("orden", 0)
        estado = tarea_datos.get("estado", "Pendiente")
        
        query = """
            INSERT INTO proceso_tareas (proceso_id, nombre, descripcion, orden, estado)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (proceso_id, tarea_datos["nombre"], descripcion, orden, estado))
        tarea_id = cursor.lastrowid
        
        conexion.commit()
        
        # Obtener la tarea recién creada
        cursor.execute("""
            SELECT * FROM proceso_tareas WHERE id = %s
        """, (tarea_id,))
        
        nueva_tarea = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        return {
            "success": True,
            "message": "Tarea creada correctamente",
            "tarea_id": tarea_id,
            "tarea": nueva_tarea
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al crear tarea: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear tarea: {str(e)}")

@app.put("/tareas/{tarea_id}", response_model=Dict[str, Any])
async def actualizar_tarea(
    tarea_id: int = Path(...),
    tarea_datos: Dict[str, Any] = Body(...)
):
    """
    Actualiza una tarea específica
    """
    try:
        conexion = conectar_db()
        if not conexion:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar que la tarea existe
        cursor.execute("SELECT * FROM proceso_tareas WHERE id = %s", (tarea_id,))
        tarea_existente = cursor.fetchone()
        
        if not tarea_existente:
            raise HTTPException(status_code=404, detail=f"Tarea con ID {tarea_id} no encontrada")
        
        # Construir la consulta de actualización dinámicamente
        campos_actualizables = ["nombre", "descripcion", "orden", "estado", "usuario_completado_id"]
        actualizar_campos = []
        valores = []
        
        for campo in campos_actualizables:
            if campo in tarea_datos:
                actualizar_campos.append(f"{campo} = %s")
                valores.append(tarea_datos[campo])
        
        # Actualizar fecha de completado si se marca como completada
        if "estado" in tarea_datos and tarea_datos["estado"] == "Completada":
            if tarea_existente["estado"] != "Completada":  # Solo si cambia a completada
                actualizar_campos.append("fecha_completado = NOW()")
        
        if not actualizar_campos:
            return {
                "success": False,
                "message": "No se proporcionaron campos para actualizar"
            }
        
        query = f"UPDATE proceso_tareas SET {', '.join(actualizar_campos)} WHERE id = %s"
        valores.append(tarea_id)
        
        cursor.execute(query, tuple(valores))
        conexion.commit()
        
        # Obtener la tarea actualizada
        cursor.execute("SELECT * FROM proceso_tareas WHERE id = %s", (tarea_id,))
        tarea_actualizada = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        return {
            "success": True,
            "message": "Tarea actualizada correctamente",
            "tarea": tarea_actualizada
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar tarea: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar tarea: {str(e)}")

@app.delete("/tareas/{tarea_id}")
async def eliminar_tarea(tarea_id: int = Path(...)):
    """
    Elimina una tarea específica
    """
    try:
        conexion = conectar_db()
        if not conexion:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Verificar que la tarea existe
        cursor.execute("SELECT id FROM proceso_tareas WHERE id = %s", (tarea_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Tarea con ID {tarea_id} no encontrada")
        
        # Eliminar la tarea
        cursor.execute("DELETE FROM proceso_tareas WHERE id = %s", (tarea_id,))
        conexion.commit()
        
        cursor.close()
        conexion.close()
        
        return {"success": True, "message": "Tarea eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al eliminar tarea: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar tarea: {str(e)}")

@app.post("/procesos/{proceso_id}/generar-tareas", response_model=Dict[str, Any])
async def generar_tareas_proceso(proceso_id: int = Path(...)):
    """
    Genera tareas predeterminadas basadas en el tipo de proceso
    """
    try:
        conexion = conectar_db()
        if not conexion:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar que el proceso existe y obtener su tipo
        cursor.execute("SELECT tipo_proceso FROM procesos2 WHERE id = %s", (proceso_id,))
        proceso = cursor.fetchone()
        
        if not proceso:
            raise HTTPException(status_code=404, detail=f"Proceso con ID {proceso_id} no encontrado")
        
        tipo_proceso = proceso['tipo_proceso']
        tareas_generadas = []
        
        # Definir tareas según el tipo de proceso
        if tipo_proceso == "APERTURA":
            tareas = [
                {"nombre": "Desactivar alarma", "descripcion": "Desactivar sistema de alarma al llegar", "orden": 1},
                {"nombre": "Encender luces", "descripcion": "Encender todas las luces del local", "orden": 2},
                {"nombre": "Verificar equipos", "descripcion": "Comprobar que todos los equipos funcionan correctamente", "orden": 3},
                {"nombre": "Preparar caja", "descripcion": "Preparar la caja registradora con cambio", "orden": 4},
                {"nombre": "Limpieza inicial", "descripcion": "Realizar limpieza rápida del área de atención", "orden": 5}
            ]
        elif tipo_proceso == "CIERRE":
            tareas = [
                {"nombre": "Cerrar caja", "descripcion": "Realizar cierre y conteo de caja", "orden": 1},
                {"nombre": "Limpieza de cierre", "descripcion": "Limpieza general del local", "orden": 2},
                {"nombre": "Apagar equipos", "descripcion": "Apagar todos los equipos electrónicos", "orden": 3},
                {"nombre": "Apagar luces", "descripcion": "Apagar todas las luces", "orden": 4},
                {"nombre": "Activar alarma", "descripcion": "Activar sistema de alarma al salir", "orden": 5}
            ]
        elif tipo_proceso == "TRASCURSO DE JORNADA" or tipo_proceso == "TRASCURSO DE LA JORNADA":
            tareas = [
                {"nombre": "Revisión de inventario", "descripcion": "Comprobar niveles de inventario", "orden": 1},
                {"nombre": "Limpieza de áreas comunes", "descripcion": "Mantener áreas comunes limpias", "orden": 2},
                {"nombre": "Control de temperatura", "descripcion": "Verificar temperaturas de equipos", "orden": 3}
            ]
        elif tipo_proceso == "PROCESO SEMANAL":
            tareas = [
                {"nombre": "Revisión semanal de stock", "descripcion": "Realizar inventario semanal completo", "orden": 1},
                {"nombre": "Limpieza profunda", "descripcion": "Realizar limpieza profunda de todas las áreas", "orden": 2},
                {"nombre": "Mantenimiento de equipos", "descripcion": "Verificar estado y funcionamiento de todos los equipos", "orden": 3},
                {"nombre": "Reunión de equipo", "descripcion": "Realizar reunión con el equipo para revisar la semana", "orden": 4}
            ]
        elif tipo_proceso == "PROCESO MENSUAL":
            tareas = [
                {"nombre": "Inventario mensual", "descripcion": "Inventario completo de productos", "orden": 1},
                {"nombre": "Revisión de objetivos", "descripcion": "Evaluar cumplimiento de objetivos del mes", "orden": 2},
                {"nombre": "Mantenimiento preventivo", "descripcion": "Realizar mantenimiento preventivo de equipos críticos", "orden": 3},
                {"nombre": "Análisis de ventas", "descripcion": "Analizar el rendimiento de ventas del mes", "orden": 4},
                {"nombre": "Planificación siguiente mes", "descripcion": "Establecer objetivos para el siguiente mes", "orden": 5}
            ]
        else:
            tareas = [
                {"nombre": "Tarea 1", "descripcion": "Descripción de la tarea 1", "orden": 1},
                {"nombre": "Tarea 2", "descripcion": "Descripción de la tarea 2", "orden": 2},
                {"nombre": "Tarea 3", "descripcion": "Descripción de la tarea 3", "orden": 3}
            ]
        
        # Insertar las tareas en la base de datos
        for tarea in tareas:
            cursor.execute("""
                INSERT INTO proceso_tareas (proceso_id, nombre, descripcion, orden, estado)
                VALUES (%s, %s, %s, %s, 'Pendiente')
            """, (proceso_id, tarea["nombre"], tarea["descripcion"], tarea["orden"]))
            
            tarea_id = cursor.lastrowid
            tarea["id"] = tarea_id
            tareas_generadas.append(tarea)
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return {
            "success": True,
            "message": f"Se generaron {len(tareas_generadas)} tareas para el proceso",
            "tareas": tareas_generadas
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al generar tareas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar tareas: {str(e)}")

@app.put("/usuarios/{id}", response_model=Dict[str, Any])
async def actualizar_usuario(id: int = Path(...), usuario: Dict[str, Any] = Body(...)):
    """
    Actualiza un usuario existente en la base de datos.
    
    - **id**: ID del usuario a actualizar
    - **usuario**: Datos del usuario a actualizar
    """
    try:
        # Connect to the database usando conexión existente
        conexion = conectar_db()
        if conexion is None:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "No se pudo conectar a la base de datos"}
            )
            
        cursor = conexion.cursor(dictionary=True)
        
        # Start building the update query
        update_query = "UPDATE usuarios SET "
        update_params = []
        query_parts = []
        
        # Add each field that needs to be updated
        if "nombre" in usuario:
            query_parts.append("Nombre = %s")
            update_params.append(usuario["nombre"])
        
        if "apellido" in usuario:
            query_parts.append("apellido = %s")
            update_params.append(usuario["apellido"])
        
        if "usuario" in usuario:
            # Check if username is already taken by another user
            check_query = "SELECT ID FROM usuarios WHERE usuario = %s AND ID != %s"
            cursor.execute(check_query, (usuario["usuario"], id))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "El nombre de usuario ya está en uso"}
                )
            
            query_parts.append("usuario = %s")
            update_params.append(usuario["usuario"])
        
        if "contraseña" in usuario and usuario["contraseña"]:
            # Hash the password before storing
            hashed_password = pwd_context.hash(usuario["contraseña"])
            query_parts.append("Contraseña = %s")  # Nota la mayúscula en "Contraseña" para coincidir con tu DB
            update_params.append(hashed_password)
        
        if "rol" in usuario:
            query_parts.append("Rol = %s")
            update_params.append(usuario["rol"])
        
        # If there's nothing to update, return early
        if not query_parts:
            return {"success": True, "message": "No hay cambios que actualizar"}
        
        # Complete the update query
        update_query += ", ".join(query_parts) + " WHERE ID = %s"
        update_params.append(id)
        
        # Execute the update
        cursor.execute(update_query, update_params)
        
        # Handle establishments if provided
        if "establecimientos" in usuario and isinstance(usuario["establecimientos"], list):
            # Delete existing user-establishment relationships
            cursor.execute("DELETE FROM usuario_establecimiento WHERE usuario_id = %s", (id,))
            
            # Insert new relationships
            for est_id in usuario["establecimientos"]:
                cursor.execute(
                    "INSERT INTO usuario_establecimiento (usuario_id, establecimiento_id) VALUES (%s, %s)",
                    (id, est_id)
                )
        
        # Commit the transaction
        conexion.commit()
        
        return {"success": True, "message": "Usuario actualizado correctamente"}
    
    except Exception as e:
        print(f"Error updating user: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error al actualizar usuario: {str(e)}"}
        )
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals() and conexion.is_connected():
            conexion.close()

@app.post("/tareas", response_model=Dict[str, Any])
async def crear_tarea(tarea_datos: Dict[str, Any] = Body(...)):
    """
    Crea una nueva tarea con datos personalizados
    """
    try:
        conexion = conectar_db()
        if not conexion:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Campos obligatorios
        if 'proceso_id' not in tarea_datos:
            raise HTTPException(status_code=400, detail="El ID del proceso es obligatorio")
            
        if 'nombre' not in tarea_datos or not tarea_datos['nombre'].strip():
            raise HTTPException(status_code=400, detail="El nombre de la tarea es obligatorio")
        
        # Verificar que el proceso existe
        proceso_id = tarea_datos['proceso_id']
        if not proceso_existe(conexion, proceso_id):
            raise HTTPException(status_code=404, detail=f"Proceso con ID {proceso_id} no encontrado")
        
        # Establecer valores predeterminados
        descripcion = tarea_datos.get("descripcion", "")
        orden = tarea_datos.get("orden", 0)
        estado = tarea_datos.get("estado", "Pendiente")
        
        query = """
            INSERT INTO proceso_tareas (proceso_id, nombre, descripcion, orden, estado)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (proceso_id, tarea_datos["nombre"], descripcion, orden, estado))
        tarea_id = cursor.lastrowid
        
        conexion.commit()
        
        # Obtener la tarea recién creada
        cursor.execute("SELECT * FROM proceso_tareas WHERE id = %s", (tarea_id,))
        nueva_tarea = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        return {
            "success": True,
            "message": "Tarea creada correctamente",
            "tarea_id": tarea_id,
            "tarea": nueva_tarea
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al crear tarea: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al crear tarea: {str(e)}")

# Función auxiliar para verificar si un proceso existe
def proceso_existe(conexion, proceso_id):
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM procesos2 WHERE id = %s", (proceso_id,))
    resultado = cursor.fetchone()
    cursor.close()
    return resultado is not None

@app.post("/tareas/{tarea_id}/imagenes")
async def upload_tarea_image(
    tarea_id: int,
    usuario_id: int = Form(...),
    imagen: UploadFile = File(...)
):
    """Upload an image to a task"""
    try:
        # Create uploads directory for task images if it doesn't exist
        task_directory = os.path.join(UPLOAD_DIR, f"tarea_{tarea_id}")
        if not os.path.exists(task_directory):
            os.makedirs(task_directory)
            
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(imagen.filename)[1]
        new_filename = f"{timestamp}_{imagen.filename}"
        file_path = os.path.join(task_directory, new_filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await imagen.read())
            
        # Create relative path for database
        relative_path = f"uploads/tarea_{tarea_id}/{new_filename}"
        
        # Insert record into database
        conn = conectar_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO tarea_imagenes 
            (tarea_id, usuario_id, ruta_imagen, nombre_imagen) 
            VALUES (%s, %s, %s, %s)
        """, (tarea_id, usuario_id, relative_path, new_filename))
        
        # Get the ID of the inserted image
        image_id = cursor.lastrowid
        conn.commit()
        
        # Get the complete image data to return
        cursor.execute("""
            SELECT ti.*, u.Nombre as nombre_usuario 
            FROM tarea_imagenes ti
            LEFT JOIN usuarios u ON ti.usuario_id = u.ID
            WHERE ti.id = %s
        """, (image_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
    
# Endpoint para eliminar una imagen de una tarea
@app.delete("/tareas/{tarea_id}/imagenes/{imagen_id}")
async def eliminar_imagen_tarea(tarea_id: int, imagen_id: int, request: Request):
    """
    Elimina una imagen asociada a una tarea
    Solo usuarios Admin y Area Manager pueden usar esta funcionalidad
    """
    # Verificar rol del usuario
    if request.state.user.get("role") not in ["Admin", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar imágenes")
    
    try:
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar que la imagen exista y pertenezca a la tarea
        cursor.execute("SELECT * FROM tarea_imagenes WHERE id = %s AND tarea_id = %s", 
                     (imagen_id, tarea_id))
        imagen = cursor.fetchone()
        
        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada o no pertenece a esta tarea")
        
        # Eliminar el archivo físico si existe
        ruta_imagen = os.path.join(os.path.dirname(__file__), imagen["ruta_imagen"])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        
        # Eliminar el registro de la base de datos
        cursor.execute("DELETE FROM tarea_imagenes WHERE id = %s", (imagen_id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": "Imagen eliminada correctamente"
        }
    
    except Exception as e:
        print(f"Error al eliminar imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar imagen: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para eliminar un comentario de una tarea
@app.delete("/tareas/{tarea_id}/comentarios/{comentario_id}")
async def eliminar_comentario_tarea(tarea_id: int, comentario_id: int, request: Request):
    """
    Elimina un comentario asociado a una tarea
    Solo usuarios Admin y Area Manager pueden usar esta funcionalidad
    """
    # Verificar rol del usuario
    if request.state.user.get("role") not in ["Admin", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar comentarios")
    
    try:
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Verificar que el comentario exista y pertenezca a la tarea
        cursor.execute("SELECT * FROM tarea_comentarios WHERE id = %s AND tarea_id = %s", 
                     (comentario_id, tarea_id))
        comentario = cursor.fetchone()
        
        if not comentario:
            raise HTTPException(status_code=404, detail="Comentario no encontrado o no pertenece a esta tarea")
        
        # Eliminar el comentario
        cursor.execute("DELETE FROM tarea_comentarios WHERE id = %s", (comentario_id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": "Comentario eliminado correctamente"
        }
    
    except Exception as e:
        print(f"Error al eliminar comentario: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar comentario: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para eliminar una imagen de un aviso
@app.delete("/avisos/{aviso_id}/imagenes/{imagen_id}")
async def eliminar_imagen_aviso(aviso_id: int, imagen_id: int, request: Request):
    """
    Elimina una imagen asociada a un aviso
    Solo usuarios Admin y Area Manager pueden usar esta funcionalidad
    """
    # Verificar rol del usuario
    if request.state.user.get("role") not in ["Admin", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar imágenes")
    
    try:
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar que la imagen exista y pertenezca al aviso
        cursor.execute("SELECT * FROM aviso_imagenes WHERE id = %s AND aviso_id = %s", 
                     (imagen_id, aviso_id))
        imagen = cursor.fetchone()
        
        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada o no pertenece a este aviso")
        
        # Eliminar el archivo físico si existe
        ruta_imagen = os.path.join(os.path.dirname(__file__), imagen["ruta_imagen"])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        
        # Eliminar el registro de la base de datos
        cursor.execute("DELETE FROM aviso_imagenes WHERE id = %s", (imagen_id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": "Imagen eliminada correctamente"
        }
    
    except Exception as e:
        print(f"Error al eliminar imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar imagen: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para eliminar un comentario de un aviso
@app.delete("/avisos/{aviso_id}/comentarios/{comentario_id}")
async def eliminar_comentario_aviso(aviso_id: int, comentario_id: int, request: Request):
    """
    Elimina un comentario asociado a un aviso
    Solo usuarios Admin y Area Manager pueden usar esta funcionalidad
    """
    # Verificar rol del usuario
    if request.state.user.get("role") not in ["Admin", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar comentarios")
    
    try:
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Verificar que el comentario exista y pertenezca al aviso
        cursor.execute("SELECT * FROM aviso_comentarios WHERE id = %s AND aviso_id = %s", 
                     (comentario_id, aviso_id))
        comentario = cursor.fetchone()
        
        if not comentario:
            raise HTTPException(status_code=404, detail="Comentario no encontrado o no pertenece a este aviso")
        
        # Eliminar el comentario
        cursor.execute("DELETE FROM aviso_comentarios WHERE id = %s", (comentario_id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": "Comentario eliminado correctamente"
        }
    
    except Exception as e:
        print(f"Error al eliminar comentario: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar comentario: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/tareas/{tarea_id}/imagenes")
async def get_tarea_images(tarea_id: int):
    """Get images for a specific task"""
    try:
        conn = conectar_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT ti.*, u.Nombre as nombre_usuario 
            FROM tarea_imagenes ti
            LEFT JOIN usuarios u ON ti.usuario_id = u.ID
            WHERE ti.tarea_id = %s
            ORDER BY ti.fecha_subida DESC
        """, (tarea_id,))
        
        imagenes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"imagenes": imagenes}
    except Exception as e:
        print(f"Error getting task images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/tareas/{tarea_id}/comentarios")
async def add_task_comment(tarea_id: int, comentario: dict):
    """Add a comment to a task"""
    try:
        conn = conectar_db()
        cursor = conn.cursor(dictionary=True)
        
        # Debug logging
        print(f"Adding comment to task {tarea_id}: {comentario}")
        
        # Get usuario_id from either field name (handle both camelCase and snake_case)
        usuario_id = comentario.get('usuario_id')  # This is what Java is sending due to @SerializedName
        if usuario_id is None:
            usuario_id = comentario.get('usuarioId')  # Try alternate name as fallback
            
        if usuario_id is None:
            raise HTTPException(status_code=400, detail="usuario_id is required")
        
        # Insert the comment
        cursor.execute("""
            INSERT INTO tarea_comentarios 
            (tarea_id, usuario_id, comentario) 
            VALUES (%s, %s, %s)
        """, (
            tarea_id,
            usuario_id,
            comentario.get('comentario')
        ))
        
        # Get the inserted comment ID
        comment_id = cursor.lastrowid
        conn.commit()
        
        # Now retrieve the complete comment data including username
        cursor.execute("""
            SELECT tc.*, u.Nombre as nombre_usuario 
            FROM tarea_comentarios tc
            LEFT JOIN usuarios u ON tc.usuario_id = u.ID
            WHERE tc.id = %s
        """, (comment_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        print(f"Error adding comment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/tareas/{tarea_id}/comentarios")
async def get_task_comments(tarea_id: int):
    """Get comments for a specific task"""
    try:
        conn = conectar_db()
        cursor = conn.cursor(dictionary=True)
        
        # Join with users table to get user names
        cursor.execute("""
            SELECT tc.*, u.Nombre as nombre_usuario 
            FROM tarea_comentarios tc
            LEFT JOIN usuarios u ON tc.usuario_id = u.ID
            WHERE tc.tarea_id = %s
            ORDER BY tc.fecha_creacion DESC
        """, (tarea_id,))
        
        comentarios = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"comentarios": comentarios}
    except Exception as e:
        print(f"Error getting comments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/establecimientos/{id}", response_model=Dict[str, Any])
async def eliminar_establecimiento(id: int = Path(...)):
    """
    Elimina un establecimiento por su ID
    """
    try:
        conexion = conectar_db()
        if not conexion:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Verificar si el establecimiento existe
        cursor.execute("SELECT * FROM establecimientos WHERE id = %s", (id,))
        establecimiento = cursor.fetchone()
        
        if not establecimiento:
            raise HTTPException(status_code=404, detail=f"Establecimiento con ID {id} no encontrado")
        
        # Eliminar el establecimiento
        cursor.execute("DELETE FROM establecimientos WHERE id = %s", (id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": f"Establecimiento con ID {id} eliminado correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar establecimiento: {str(e)}")
    
    finally:
        if 'conexion' in locals() and conexion:
            conexion.close()

# Endpoint para eliminar una imagen de una tarea
@app.delete("/tareas/{tarea_id}/imagenes/{imagen_id}")
async def eliminar_imagen_tarea(tarea_id: int, imagen_id: int, request: Request):
    """
    Elimina una imagen asociada a una tarea
    Solo usuarios Admin y Area Manager pueden usar esta funcionalidad
    """
    # Verificar rol del usuario
    if request.state.user.get("role") not in ["Admin", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar imágenes")
    
    try:
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar que la imagen exista y pertenezca a la tarea
        cursor.execute("SELECT * FROM tarea_imagenes WHERE id = %s AND tarea_id = %s", 
                     (imagen_id, tarea_id))
        imagen = cursor.fetchone()
        
        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada o no pertenece a esta tarea")
        
        # Eliminar el archivo físico si existe
        ruta_imagen = os.path.join(os.path.dirname(__file__), imagen["ruta_imagen"])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        
        # Eliminar el registro de la base de datos
        cursor.execute("DELETE FROM tarea_imagenes WHERE id = %s", (imagen_id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": "Imagen eliminada correctamente"
        }
    
    except Exception as e:
        print(f"Error al eliminar imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar imagen: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para eliminar un comentario de una tarea
@app.delete("/tareas/{tarea_id}/comentarios/{comentario_id}")
async def eliminar_comentario_tarea(tarea_id: int, comentario_id: int, request: Request):
    """
    Elimina un comentario asociado a una tarea
    Solo usuarios Admin y Area Manager pueden usar esta funcionalidad
    """
    # Verificar rol del usuario
    if request.state.user.get("role") not in ["Admin", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar comentarios")
    
    try:
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Verificar que el comentario exista y pertenezca a la tarea
        cursor.execute("SELECT * FROM tarea_comentarios WHERE id = %s AND tarea_id = %s", 
                     (comentario_id, tarea_id))
        comentario = cursor.fetchone()
        
        if not comentario:
            raise HTTPException(status_code=404, detail="Comentario no encontrado o no pertenece a esta tarea")
        
        # Eliminar el comentario
        cursor.execute("DELETE FROM tarea_comentarios WHERE id = %s", (comentario_id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": "Comentario eliminado correctamente"
        }
    
    except Exception as e:
        print(f"Error al eliminar comentario: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar comentario: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para eliminar una imagen de un aviso
@app.delete("/avisos/{aviso_id}/imagenes/{imagen_id}")
async def eliminar_imagen_aviso(aviso_id: int, imagen_id: int, request: Request):
    """
    Elimina una imagen asociada a un aviso
    Solo usuarios Admin y Area Manager pueden usar esta funcionalidad
    """
    # Verificar rol del usuario
    if request.state.user.get("role") not in ["Admin", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar imágenes")
    
    try:
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor(dictionary=True)
        
        # Verificar que la imagen exista y pertenezca al aviso
        cursor.execute("SELECT * FROM aviso_imagenes WHERE id = %s AND aviso_id = %s", 
                     (imagen_id, aviso_id))
        imagen = cursor.fetchone()
        
        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada o no pertenece a este aviso")
        
        # Eliminar el archivo físico si existe
        ruta_imagen = os.path.join(os.path.dirname(__file__), imagen["ruta_imagen"])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        
        # Eliminar el registro de la base de datos
        cursor.execute("DELETE FROM aviso_imagenes WHERE id = %s", (imagen_id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": "Imagen eliminada correctamente"
        }
    
    except Exception as e:
        print(f"Error al eliminar imagen: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar imagen: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Endpoint para eliminar un comentario de un aviso
@app.delete("/avisos/{aviso_id}/comentarios/{comentario_id}")
async def eliminar_comentario_aviso(aviso_id: int, comentario_id: int, request: Request):
    """
    Elimina un comentario asociado a un aviso
    Solo usuarios Admin y Area Manager pueden usar esta funcionalidad
    """
    # Verificar rol del usuario
    if request.state.user.get("role") not in ["Admin", "Area Manager"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar comentarios")
    
    try:
        conexion = conectar_db()
        if conexion is None:
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
            
        cursor = conexion.cursor()
        
        # Verificar que el comentario exista y pertenezca al aviso
        cursor.execute("SELECT * FROM aviso_comentarios WHERE id = %s AND aviso_id = %s", 
                     (comentario_id, aviso_id))
        comentario = cursor.fetchone()
        
        if not comentario:
            raise HTTPException(status_code=404, detail="Comentario no encontrado o no pertenece a este aviso")
        
        # Eliminar el comentario
        cursor.execute("DELETE FROM aviso_comentarios WHERE id = %s", (comentario_id,))
        conexion.commit()
        
        return {
            "success": True,
            "message": "Comentario eliminado correctamente"
        }
    
    except Exception as e:
        print(f"Error al eliminar comentario: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar comentario: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

async def generar_procesos_diarios_v2():
    """Genera procesos diarios de tipo APERTURA, CIERRE y TRASCURSO DE JORNADA para todos los establecimientos"""
    conexion = conectar_db()
    if conexion is None:
        print("Error: No se pudo conectar a la base de datos")
        return
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Obtener establecimientos activos con su nombre
        cursor.execute("SELECT id, nombre FROM Establecimientos WHERE estado = 'activo'")
        establecimientos = cursor.fetchall()
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        # Tipos de procesos diarios
        tipos_diarios = ["APERTURA", "CIERRE", "TRASCURSO DE JORNADA"]
        
        # Horarios para cada tipo (ejemplos)
        horarios = {
            "APERTURA": "07:00",
            "CIERRE": "7:00",
            "TRASCURSO DE JORNADA": "7:00"
        }
        
        # Por cada establecimiento, crear los tres tipos de procesos diarios
        for establecimiento in establecimientos:
            for tipo in tipos_diarios:
                # Datos para el proceso
                datos_proceso = {
                    "tipo_proceso": tipo,
                    "descripcion": f"Proceso de {tipo}",
                    "frecuencia": "Diaria",
                    "horario": horarios[tipo],
                    "fecha_inicio": fecha_actual,
                    "fecha_fin": fecha_actual,
                    "estado": "Verificación pendiente",
                    "ubicacion": establecimiento["nombre"],
                    "establecimiento_id": establecimiento["id"],
                    "usuario_id": None  # Sistema automático
                }
                
                # Insertar el proceso en la tabla procesos2
                cursor.execute("""
                    INSERT INTO procesos2 (tipo_proceso, descripcion, frecuencia, horario, 
                    fecha_inicio, fecha_fin, estado, ubicacion, establecimiento_id, usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    datos_proceso["tipo_proceso"],
                    datos_proceso["descripcion"],
                    datos_proceso["frecuencia"],
                    datos_proceso["horario"],
                    datos_proceso["fecha_inicio"],
                    datos_proceso["fecha_fin"],
                    datos_proceso["estado"],
                    datos_proceso["ubicacion"],
                    datos_proceso["establecimiento_id"],
                    datos_proceso["usuario_id"]
                ))
        
        conexion.commit()
        print(f"Procesos diarios generados exitosamente para {len(establecimientos)} establecimientos")
    except Exception as e:
        print(f"Error al generar procesos diarios: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

async def generar_procesos_semanales_v2():
    """Genera procesos semanales para todos los establecimientos activos"""
    conexion = conectar_db()
    if conexion is None:
        print("Error: No se pudo conectar a la base de datos")
        return
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Obtener establecimientos activos con su nombre
        cursor.execute("SELECT id, nombre FROM Establecimientos WHERE estado = 'activo'")
        establecimientos = cursor.fetchall()
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        hora_actual = "07:00"  # Hora fija para procesos semanales
        
        # Calcular la fecha de fin (una semana después)
        fecha_fin = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Por cada establecimiento, crear proceso semanal
        for establecimiento in establecimientos:
            # Datos para el proceso semanal
            datos_proceso = {
                "tipo_proceso": "PROCESO SEMANAL",
                "descripcion": f"Proceso de SEMANAL",
                "frecuencia": "Semanal",
                "horario": hora_actual,
                "fecha_inicio": fecha_actual,
                "fecha_fin": fecha_fin,
                "estado": "Verificación pendiente",
                "ubicacion": establecimiento["nombre"],
                "establecimiento_id": establecimiento["id"],
                "usuario_id": None
            }
            
            # Insertar el proceso en la tabla procesos2
            cursor.execute("""
                INSERT INTO procesos2 (tipo_proceso, descripcion, frecuencia, horario, 
                fecha_inicio, fecha_fin, estado, ubicacion, establecimiento_id, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                datos_proceso["tipo_proceso"],
                datos_proceso["descripcion"],
                datos_proceso["frecuencia"],
                datos_proceso["horario"],
                datos_proceso["fecha_inicio"],
                datos_proceso["fecha_fin"],
                datos_proceso["estado"],
                datos_proceso["ubicacion"],
                datos_proceso["establecimiento_id"],
                datos_proceso["usuario_id"]
            ))
        
        conexion.commit()
        print(f"Procesos semanales generados exitosamente para {len(establecimientos)} establecimientos")
    except Exception as e:
        print(f"Error al generar procesos semanales: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

async def generar_procesos_mensuales_v2():
    """Genera procesos mensuales para todos los establecimientos activos"""
    conexion = conectar_db()
    if conexion is None:
        print("Error: No se pudo conectar a la base de datos")
        return
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Obtener establecimientos activos con su nombre
        cursor.execute("SELECT id, nombre FROM Establecimientos WHERE estado = 'activo'")
        establecimientos = cursor.fetchall()
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        hora_actual = "7:00"  # Hora fija para procesos mensuales
        
        # Calcular la fecha de fin (un mes después aproximadamente)
        fecha_fin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Por cada establecimiento, crear proceso mensual
        for establecimiento in establecimientos:
            # Datos para el proceso mensual
            datos_proceso = {
                "tipo_proceso": "PROCESO MENSUAL",
                "descripcion": f"Proceso de MENSUAL",
                "frecuencia": "Mensual",
                "horario": hora_actual,
                "fecha_inicio": fecha_actual,
                "fecha_fin": fecha_fin,
                "estado": "Verificación pendiente",
                "ubicacion": establecimiento["nombre"],
                "establecimiento_id": establecimiento["id"],
                "usuario_id": None
            }
            
            # Insertar el proceso en la tabla procesos2
            cursor.execute("""
                INSERT INTO procesos2 (tipo_proceso, descripcion, frecuencia, horario, 
                fecha_inicio, fecha_fin, estado, ubicacion, establecimiento_id, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                datos_proceso["tipo_proceso"],
                datos_proceso["descripcion"],
                datos_proceso["frecuencia"],
                datos_proceso["horario"],
                datos_proceso["fecha_inicio"],
                datos_proceso["fecha_fin"],
                datos_proceso["estado"],
                datos_proceso["ubicacion"],
                datos_proceso["establecimiento_id"],
                datos_proceso["usuario_id"]
            ))
        
        conexion.commit()
        print(f"Procesos mensuales generados exitosamente para {len(establecimientos)} establecimientos")
    except Exception as e:
        print(f"Error al generar procesos mensuales: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

@app.get("/establecimientos/usuario/{usuario_id}")
def obtener_establecimientos_por_usuario(usuario_id: int = Path(...)):
    """
    Obtiene los establecimientos asignados a un usuario específico usando parámetro de ruta
    """
    conexion = conectar_db()
    if conexion is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT e.* FROM Establecimientos e
        JOIN usuario_establecimiento ue ON e.id = ue.establecimiento_id
        WHERE ue.usuario_id = %s
        """
        cursor.execute(query, (usuario_id,))
        establecimientos = cursor.fetchall()
        
        # Formatear los resultados para garantizar consistencia
        formatted_establecimientos = []
        for establecimiento in establecimientos:
            formatted_establecimiento = {
                "id": establecimiento.get('id') or establecimiento.get('ID'),
                "nombre": establecimiento.get('nombre') or establecimiento.get('Nombre'),
                "direccion": establecimiento.get('direccion') or establecimiento.get('Direccion', ''),
                "tipo": establecimiento.get('tipo') or establecimiento.get('Tipo', ''),
                "estado": establecimiento.get('estado') or establecimiento.get('Estado', '')
            }
            formatted_establecimientos.append(formatted_establecimiento)
        
        return {"establecimientos": formatted_establecimientos}
    except Error as e:
        print(f"Error al consultar establecimientos para usuario {usuario_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Configurar el planificador para la tabla procesos2
scheduler = AsyncIOScheduler()

# Programar las tareas automáticas
scheduler.add_job(generar_procesos_diarios_v2, CronTrigger(hour=9, minute=30))  # Cada día a las 7:00 AM
scheduler.add_job(generar_procesos_semanales_v2, CronTrigger(day_of_week='mon', hour=7, minute=0))  # Cada lunes a las 8:00 AM
scheduler.add_job(generar_procesos_mensuales_v2, CronTrigger(day=1, hour=7, minute=0))  # El primer día de cada mes a las 9:00 AM

# Añade este evento de inicio para la aplicación
@app.on_event("startup")
async def startup_event():
    print("Iniciando scheduler para generación automática de procesos...")
    scheduler.start()
    print("Scheduler iniciado correctamente")

# ===== NUEVOS ENDPOINTS PARA GESTIÓN DE TAREAS =====
