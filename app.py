from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response
from models import db, Workshop, Attendee, User
from flask_bcrypt import Bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///talleres.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super_secret_key_change_this_in_production'  # Importante para JWT

db.init_app(app)
bcrypt = Bcrypt(app)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # 1. Intentar obtener token de la cookie (para navegadores)
        if 'token' in request.cookies:
            token = request.cookies.get('token')
        # 2. O del Header (para clientes API puros como Postman)
        elif 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            # Si es una petición de navegador, redirigir a login
            if 'text/html' in request.accept_mimetypes:
                return redirect(url_for('login_page'))
            return jsonify({'message': 'Token faltante'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.session.get(User, data['user_id'])
            if not current_user or not current_user.is_admin:
                raise Exception("Acceso denegado")
        except:
            if 'text/html' in request.accept_mimetypes:
                return redirect(url_for('login_page'))
            return jsonify({'message': 'Token inválido o expirado'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Maneja el login y la generación del JWT en cookie."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # Generar Token JWT
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Expira en 2 horas
            }, app.config['SECRET_KEY'], algorithm="HS256")

            # Crear respuesta y setear cookie
            resp = make_response(redirect(url_for('view_admin')))
            resp.set_cookie('token', token, httponly=True)  # httponly por seguridad
            return resp

        return render_template('login.html', error="Credenciales inválidas")

    return render_template('login.html')


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('view_students')))
    resp.set_cookie('token', '', expires=0)  # Borrar cookie
    return resp

@app.route('/')
def view_students():
    workshops = Workshop.query.all()
    # Chequeamos si hay usuario logueado solo para mostrar el botón de "Ir al Admin" o "Logout" en el navbar
    is_admin = False
    if 'token' in request.cookies:
        try:
            jwt.decode(request.cookies.get('token'), app.config['SECRET_KEY'], algorithms=["HS256"])
            is_admin = True
        except:
            pass
    return render_template('index.html', workshops=workshops, is_admin=is_admin)


@app.route('/api/workshops', methods=['GET'])
def api_get_workshops():
    workshops = Workshop.query.all()
    return jsonify([w.to_dict() for w in workshops]), 200


@app.route('/api/workshops/<int:id>', methods=['GET'])
def api_get_workshop_detail(id):
    workshop = db.session.get(Workshop, id)
    if not workshop:
        return jsonify({"error": "Taller no encontrado"}), 404
    return jsonify(workshop.to_dict()), 200


@app.route('/api/workshops/<int:id>/register', methods=['POST'])
def api_register_student(id):
    # Registro público
    data = request.json
    student_name = data.get('student_name')
    workshop = db.session.get(Workshop, id)
    if not workshop:
        return jsonify({"error": "Taller no encontrado"}), 404
    new_attendee = Attendee(student_name=student_name, workshop_id=id)
    db.session.add(new_attendee)
    db.session.commit()
    return jsonify({"message": f"Estudiante {student_name} registrado exitosamente"}), 201


# --- PROTECTED ADMIN ROUTES (Views & API) ---

@app.route('/admin')
@admin_required  # <--- PROTECTION ADDED
def view_admin():
    workshops = Workshop.query.all()
    return render_template('admin.html', workshops=workshops, is_admin=True)


@app.route('/admin/create', methods=['POST'])
@admin_required  # <--- PROTECTION ADDED
def web_create_workshop():
    new_workshop = Workshop(
        name=request.form['name'],
        description=request.form['description'],
        date=request.form['date'],
        time=request.form['time'],
        location=request.form['location'],
        category=request.form['category']
    )
    db.session.add(new_workshop)
    db.session.commit()
    return redirect(url_for('view_admin'))


@app.route('/admin/edit/<int:id>', methods=['POST'])
@admin_required  # <--- PROTECTION ADDED
def web_edit_workshop(id):
    workshop = db.session.get(Workshop, id)
    if workshop:
        workshop.name = request.form['name']
        workshop.description = request.form['description']
        workshop.date = request.form['date']
        workshop.time = request.form['time']
        workshop.location = request.form['location']
        workshop.category = request.form['category']
        db.session.commit()
    return redirect(url_for('view_admin'))


@app.route('/admin/delete/<int:id>')
@admin_required  # <--- PROTECTION ADDED
def web_delete_workshop(id):
    workshop = db.session.get(Workshop, id)
    if workshop:
        db.session.delete(workshop)
        db.session.commit()
    return redirect(url_for('view_admin'))


# Protected APIs (For external tools or if you convert to JS frontend later)
@app.route('/api/workshops', methods=['POST'])
@admin_required
def api_create_workshop():
    data = request.json
    new_workshop = Workshop(
        name=data['name'],
        description=data.get('description', ''),
        date=data['date'],
        time=data['time'],
        location=data['location'],
        category=data['category']
    )
    db.session.add(new_workshop)
    db.session.commit()
    return jsonify(new_workshop.to_dict()), 201


@app.route('/api/workshops/<int:id>', methods=['PUT', 'DELETE'])
@admin_required
def api_modify_workshop(id):
    workshop = db.session.get(Workshop, id)
    if not workshop:
        return jsonify({"error": "Taller no encontrado"}), 404

    if request.method == 'DELETE':
        db.session.delete(workshop)
        db.session.commit()
        return jsonify({"message": "Taller eliminado"}), 200

    # PUT
    data = request.json
    workshop.name = data.get('name', workshop.name)
    # ... update fields ...
    db.session.commit()
    return jsonify(workshop.to_dict()), 200


# Creates initial admin user if not exists
@app.before_request
def create_initial_admin():
    if not User.query.first():
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(username='admin', password=hashed_pw, is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print(">>> Usuario Admin creado: admin / admin123")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)