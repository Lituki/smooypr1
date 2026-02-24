@echo off
echo Activando entorno virtual...
call C:\Users\Asia_Coordinator\Desktop\FastAPI\fastapi-env\Scripts\activate.bat

echo Iniciando servidor FastAPI...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause


