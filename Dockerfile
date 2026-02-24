FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install python-multipart
RUN pip install fastapi uvicorn mysql-connector-python passlib[bcrypt] python-jose[cryptography] apscheduler

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
