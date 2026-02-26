# =============================================================================
# config.py — CONFIGURACIÓN CENTRAL DE LA APLICACIÓN
# =============================================================================
#
# ¿QUÉ HACE ESTE ARCHIVO?
# Lee todas las variables del archivo .env y las expone al resto de la app
# a través del objeto `settings`. Es el ÚNICO sitio donde se accede a las
# variables de entorno. El resto de archivos importan desde aquí.
#
# ¿POR QUÉ HACERLO ASÍ?
# Sin este archivo, las credenciales están hardcodeadas en main.py o
# duplicadas en varios sitios. Con este archivo:
#   - Un único punto de verdad para toda la configuración.
#   - Si cambias una variable en .env, el cambio se propaga a toda la app.
#   - Fácil de testear: puedes pasar un .env diferente para tests.
#
# CÓMO SE USA EN OTROS ARCHIVOS:
#   from config import settings
#
#   # Luego usas los valores así:
#   settings.db_password       → contraseña de la base de datos
#   settings.jwt_secret_key    → clave secreta JWT
#   settings.cors_origins_list → lista de orígenes CORS
#
# =============================================================================

import secrets
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Clase de configuración. Pydantic lee automáticamente cada campo
    desde la variable de entorno con el mismo nombre (en mayúsculas).
    
    Si una variable obligatoria falta en el .env, la app lanzará un error
    claro en el arranque en lugar de fallar de forma misteriosa después.
    """

    # -------------------------------------------------------------------------
    # BASE DE DATOS
    # -------------------------------------------------------------------------
    db_host: str = "127.0.0.1"
    db_name: str
    db_user: str
    db_password: str
    db_port: int = 3306

    # -------------------------------------------------------------------------
    # JWT
    # -------------------------------------------------------------------------
    # Campo obligatorio: si no está en el .env, la app no arranca.
    # Esto es intencional — no queremos que corra sin una clave real.
    jwt_secret_key: str

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 525600

    # -------------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------------
    # En el .env los orígenes vienen como string separado por comas.
    # La propiedad cors_origins_list (ver abajo) lo convierte en lista.
    cors_origins: str = "http://localhost:5500"

    # -------------------------------------------------------------------------
    # Configuración de Pydantic
    # -------------------------------------------------------------------------
    class Config:
        # Le decimos a Pydantic dónde está el archivo de entorno.
        env_file = ".env"
        # Ignorar mayúsculas/minúsculas en los nombres de variables.
        case_sensitive = False

    # -------------------------------------------------------------------------
    # Propiedades calculadas (no vienen del .env, se derivan de otras)
    # -------------------------------------------------------------------------
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convierte el string de CORS_ORIGINS en una lista de Python.
        
        En .env: CORS_ORIGINS=http://localhost:5500,http://ejemplo.com
        Resultado: ["http://localhost:5500", "http://ejemplo.com"]
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]


# =============================================================================
# INSTANCIA GLOBAL
# =============================================================================
# Se crea UNA SOLA VEZ al importar este módulo.
# El resto de la aplicación hace: from config import settings
#
# Al instanciar Settings(), Pydantic:
#   1. Lee el archivo .env
#   2. Valida que todos los campos obligatorios estén presentes
#   3. Convierte los tipos (por ejemplo, DB_PORT="3306" → int 3306)
#   4. Lanza un error descriptivo si algo falta o tiene el tipo incorrecto
# =============================================================================
settings = Settings()


# =============================================================================
# VALIDACIÓN EN EL ARRANQUE
# =============================================================================
# Comprobaciones adicionales que Pydantic no puede hacer automáticamente.
# Se ejecutan una sola vez cuando Python importa este módulo.

def _validar_configuracion():
    """
    Valida que la configuración sea segura antes de que la app arranque.
    Si algo está mal, lanza un error con un mensaje claro.
    """
    errores = []

    # Comprobar que la SECRET_KEY no sea uno de los valores de ejemplo
    # que estaban hardcodeados en el código original.
    claves_inseguras = [
        "tu_clave_secreta_aqui",
        "tu_clave_secreta_compleja_aqui",
        "genera_una_clave_aleatoria_aqui",
        "REEMPLAZA_ESTO_CON_TU_CLAVE_GENERADA",
        "secret",
        "password",
        "",
    ]
    if settings.jwt_secret_key in claves_inseguras:
        errores.append(
            "JWT_SECRET_KEY tiene un valor inseguro o de ejemplo. "
            "Genera una clave real con: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Comprobar longitud mínima de la clave
    if len(settings.jwt_secret_key) < 32:
        errores.append(
            f"JWT_SECRET_KEY es demasiado corta ({len(settings.jwt_secret_key)} caracteres). "
            "Debe tener al menos 32 caracteres."
        )

    # Comprobar que la contraseña de BD no esté vacía
    if not settings.db_password:
        errores.append("DB_PASSWORD está vacía.")

    # Si hay errores, mostrarlos todos juntos y detener el arranque
    if errores:
        mensaje = "\n".join(f"  ❌ {e}" for e in errores)
        raise ValueError(
            f"\n\n{'='*60}\n"
            f"ERROR DE CONFIGURACIÓN — La app no puede arrancar:\n"
            f"{mensaje}\n"
            f"\nRevisa tu archivo .env\n"
            f"{'='*60}\n"
        )

    print("✅ Configuración validada correctamente.")


# Ejecutar la validación al importar el módulo
_validar_configuracion()