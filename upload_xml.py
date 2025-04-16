import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/', methods=['GET'])
def index():
    """Стартовая страница."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_xml():
    """Загрузка xml-файла."""
    if 'xml_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Файл не выбран'})

    file = request.files['xml_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Файл не выбран'})

    if not file.filename.endswith('.xml'):
        return jsonify({'status': 'error', 'message': 'Только XML-файлы'})

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    if os.path.exists(filepath):
        return jsonify(
            {'status': 'error', 'message': 'Такой файл уже существует'}
        )

    try:
        file.save(filepath)
        return jsonify(
            {'status': 'success', 'message': 'Файл успешно загружен'}
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Ошибка: {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True)
