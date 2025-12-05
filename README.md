# 🎓 Sistema de Gestión de Talleres de Formación

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0-000000?logo=flask)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap)
![Status](https://img.shields.io/badge/Status-Prototipo_Funcional-success)

## 📋 Descripción

Aplicación web Full Stack diseñada para gestionar talleres de formación profesional (cursos técnicos, capacitaciones, etc.). 

El sistema permite a los **estudiantes** consultar y registrarse en talleres, y a los **administradores** gestionar el ciclo de vida de los mismos (crear, editar, eliminar) a través de un panel de control o mediante una **API RESTful** integrada.

## 🚀 Características

### 🔹 Funcionalidades Web
* **Vista Estudiantes:** Listado de talleres disponibles con detalles (fecha, hora, lugar) y botón de inscripción.
* **Vista Administrador:** Panel de gestión (Dashboard) con tablas para ver, crear y eliminar talleres.
* **Interfaz:** Diseño responsivo utilizando **Bootstrap 5**.

### 🔹 API RESTful
Backend robusto que expone endpoints para integración externa:
* `GET /workshops`: Listar todos los talleres.
* `POST /workshops`: Crear nuevos talleres.
* `DELETE /workshops/{id}`: Eliminar talleres.
* `POST /workshops/{id}/register`: Registrar asistencia.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python, Flask
* **Base de Datos:** SQLite (vía SQLAlchemy ORM)
* **Frontend:** HTML5, Jinja2, Bootstrap 5
* **Testing:** Pytest

## 📂 Estructura del Proyecto

```text
gestion_talleres/
├── templates/
│   ├── base.html        # Layout principal (Navbar)
│   ├── index.html       # Vista pública (Estudiantes)
│   └── admin.html       # Vista privada (Administradores)
├── app.py               # Lógica de la aplicación y API
├── models.py            # Modelos de Base de Datos
├── test_app.py          # Pruebas Unitarias
├── requirements.txt     # Dependencias
└── README.md            # Documentación
