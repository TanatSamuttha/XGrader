import os
from flask import Flask, request, url_for, render_template, session, send_from_directory, redirect
from werkzeug.utils import secure_filename
import uuid
import scanner
import gradeAI

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ตั้งค่าพาธสำหรับโฟลเดอร์ uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# สร้างโฟลเดอร์ uploads หากไม่มี
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

answer = []


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['user_id'])
    os.makedirs(user_folder, exist_ok=True)

    # ดึงค่าจาก session
    image_url = session.get('image_url')
    image_urls2 = session.get('image_urls2', [])

    if request.method == 'POST':
        global answer

        # อัปโหลดไฟล์ AnswerKey (image1)
        if 'image1' in request.files:
            file = request.files['image1']
            if file and file.filename:
                filename = secure_filename("AnswerKey.png")
                file_path = os.path.join(user_folder, filename)
                file.save(file_path)
                try:
                    scanner.main(file_path)  # เรียกใช้ scanner
                    answer = gradeAI.answerkeyscan(file_path)  # สแกนคำตอบ
                    image_url = url_for('uploaded_file', filename=f"{session['user_id']}/{filename}")
                    session['image_url'] = image_url
                except Exception as e:
                    print(f"Error processing AnswerKey: {e}")
                    return redirect(request.url)

        # อัปโหลดไฟล์อื่นๆ (image2)
        if 'image2' in request.files:
            files = request.files.getlist('image2')
            image_urls2 = []
            for index, file in enumerate(files):
                if file and file.filename:
                    filename = secure_filename(f"Answer_{index + 1}.png")
                    file_path = os.path.join(user_folder, filename)
                    file.save(file_path)
                    try:
                        scanner.main(file_path)  # สแกนไฟล์
                        print(gradeAI.grading(file_path, answer))  # ประเมินคะแนน
                        image_url2 = url_for('uploaded_file', filename=f"{session['user_id']}/{filename}")
                        image_urls2.append(image_url2)
                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")

            session['image_urls2'] = image_urls2

    return render_template('index.html', image_url=image_url, image_urls2=image_urls2)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True)
