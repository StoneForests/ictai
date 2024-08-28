import os
import time
from multiprocessing import Process, Manager

from flask import Flask, render_template, request, jsonify, send_from_directory

from util.log import logger

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def run_excel_task(file_path, directory_files, task_id, progress_dict):
    from excel import Excel
    excel = Excel(file_path, directory_files)

    def update_progress(value):
        progress_dict[task_id] = value  # 更新共享进度字典

    new_file_path = excel.execute(progress_callback=update_progress)  # 生成新文件
    return new_file_path  # 返回生成的新文件路径


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start_analysis', methods=['POST'])
def start_analysis():
    ict_file = request.files['ict_file']
    directory_files = request.files.getlist('directory_files')

    if ict_file and directory_files:
        ict_file_path = os.path.join(app.config['UPLOAD_FOLDER'], ict_file.filename)
        ict_file.save(ict_file_path)

        directory_path = os.path.join(app.config['UPLOAD_FOLDER'], 'directory_files')
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        for file in directory_files:
            file.save(os.path.join(directory_path, file.filename))

        logger.info(f"Excel文件路径: {ict_file_path}")
        logger.info(f"自研成本测算文件目录: {directory_path}")

        task_id = str(time.time())
        progress_dict[task_id] = 0

        process = Process(target=run_excel_task, args=(ict_file_path, directory_path, task_id, progress_dict))
        process.start()

        # 生成新文件名
        original_filename, file_extension = os.path.splitext(ict_file.filename)
        new_filename = f"{original_filename}_分析后{file_extension}"

        return jsonify({"status": "success", "task_id": task_id, "filename": new_filename})
    else:
        return jsonify({"status": "error", "message": "请上传文件并选择目录"})


@app.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    progress = progress_dict.get(task_id, 0)
    return jsonify({"progress": progress})


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    manager = Manager()
    progress_dict = manager.dict()  # 使用Manager管理共享字典
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5000)
