from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# การกำหนดค่าฐานข้อมูล
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_BINDS'] = {
    'patients': 'sqlite:///info.db'  # ฐานข้อมูลผู้ป่วย
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '1234'  # สำหรับการจัดการเซสชัน
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
    surname = db.Column(db.String(150), nullable=False)  # นามสกุล
    dental_num = db.Column(db.String(50), nullable=False)  # หมายเลขทันตกรรม
    diagnosis = db.Column(db.String(255), nullable=True)  # การวินิจฉัย
    icd10 = db.Column(db.String(10), nullable=True)  # รหัส ICD-10
    visit_type = db.Column(db.String(50), nullable=False)  # ประเภทการเยี่ยมชม
    date = db.Column(db.Date, nullable=False)  # วันที่
    
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

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        dental_num = request.form.get('dental_num')
        diagnosis = request.form.get('diagnosis')
        icd10 = request.form.get('icd10')
        visit_type = request.form.get('visit_type')
        date_str = request.form.get('date')  # Get the date as a string

        # Convert the date string to a date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_patient = Patient(
            name=name,
            surname=surname,
            dental_num=dental_num,
            diagnosis=diagnosis,
            icd10=icd10,
            visit_type=visit_type,
            date=date  # Use the date object here
        )
        db.session.add(new_patient)
        db.session.commit()

        flash("เพิ่มสำเร็จ!")  # Flash a success message
        return redirect(url_for('main'))
    
    # If it's a GET request, render add.html
    return render_template('add.html')

# สร้างตาราง
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
