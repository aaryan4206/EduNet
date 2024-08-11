import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)
app.secret_key = 'flaskapp.pass'

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def create_connection():
    return mysql.connector.connect(host="localhost", user="root", password="mysql.pass", database="mydatabase")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uid = request.form['uid']
        upass = request.form['upass']
        db = create_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM USERS WHERE UID=%s AND UPASS=%s", (uid, upass))
        user = cursor.fetchone()
        if user:
            session['uname'] = user[1]
            session['uid'] = uid
            session['role'] = user[3]  # Assuming role is in the 4th column
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid User ID or Password!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'uid' not in session:
        return redirect(url_for('login'))
    
    db = create_connection()
    cursor = db.cursor()
    uid = session['uid']
    avail_class = []
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for (table_name,) in tables:
        if table_name.endswith("_MESSAGES") or table_name.endswith("_PDFS") or table_name == "USERS":
            continue
        else:
            query = f"SELECT '{table_name}' AS table_name FROM {table_name} WHERE UID = {uid}"
            cursor.execute(query)
            result = cursor.fetchall()
            if result:
                avail_class.append(result[0][0])
    
    return render_template('home.html', avail_class=avail_class, role=session['role'])

@app.route('/send_message/<class_name>', methods=['GET', 'POST'])
def send_message(class_name):
    if 'uid' not in session or session['role'] != 'TEACHER':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        message = request.form['message']
        db = create_connection()
        cursor = db.cursor()
        query = f"INSERT INTO {class_name}_MESSAGES (message) VALUES(%s)"
        cursor.execute(query, (message,))
        db.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('view_messages', class_name=class_name))
    
    return render_template('send_message.html', class_name=class_name)

@app.route('/view_messages/<class_name>')
def view_messages(class_name):
    if 'uid' not in session:
        return redirect(url_for('login'))
    
    db = create_connection()
    cursor = db.cursor()
    query = f"SELECT * FROM {class_name}_MESSAGES"
    cursor.execute(query)
    messages = cursor.fetchall()
    
    return render_template('view_messages.html', class_name=class_name, messages=messages)

@app.route('/upload_pdf/<class_name>', methods=['GET', 'POST'])
def upload_pdf(class_name):
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            db = create_connection()
            cursor = db.cursor()
            query = f"INSERT INTO {class_name}_PDFS (filename, filepath) VALUES (%s, %s)"
            cursor.execute(query, (filename, filepath))
            db.commit()
            cursor.close()
            db.close()

            flash('File successfully uploaded')
            return redirect(url_for('view_pdfs', class_name=class_name))
    
    return render_template('upload_pdf.html', class_name=class_name)

# Route to view PDFs
@app.route('/view_pdfs/<class_name>')
def view_pdfs(class_name):
    db = create_connection()
    cursor = db.cursor()
    query = f"SELECT id, filename, upload_time FROM {class_name}_PDFS"
    cursor.execute(query)
    pdfs = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('view_pdfs.html', class_name=class_name, pdfs=pdfs)

# Route to download PDF
@app.route('/download_pdf/<class_name>/<int:pdf_id>')
def download_pdf(class_name, pdf_id):
    db = create_connection()
    cursor = db.cursor()
    query = f"SELECT filepath FROM {class_name}_PDFS WHERE id = %s"
    cursor.execute(query, (pdf_id,))
    pdf = cursor.fetchone()
    cursor.close()
    db.close()
    
    if pdf:
        return send_file(pdf[0], as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('view_pdfs', class_name=class_name))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
