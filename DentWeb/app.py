from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# การกำหนดค่าฐานข้อมูล
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_BINDS'] = {
    'patients': 'sqlite:///info.db'  # ฐานข้อมูลผู้ป่วย
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '1234'  #สำหรับการจัดการเซสชัน
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Patient(db.Model):
    __bind_key__ = 'patients'  # ใช้ฐานข้อมูลผู้ป่วย
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    age = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
        if user and user.check_password(password):
            return jsonify(success=True)
        else:
            return jsonify(success=False, message="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง.")
    return render_template('login.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')

        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            return {"success": False, "message": "อีเมลหรือชื่อผู้ใช้นี้มีอยู่แล้ว."}, 400

        new_user = User(email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return {"success": True, "message": "ลงทะเบียนสำเร็จ!"}, 200
    return render_template('reg.html')

@app.route('/main')
def main():
    patients = Patient.query.all()  # ดึงข้อมูลผู้ป่วยทั้งหมด
    return render_template('main.html', patients=patients)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    phone = request.form.get('phone')
    age = request.form.get('age')

    new_patient = Patient(name=name, phone=phone, age=int(age))
    db.session.add(new_patient)
    db.session.commit()

    flash("เพิ่มสำเร็จ!")
    return redirect(url_for('main'))

# สร้างตาราง
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
