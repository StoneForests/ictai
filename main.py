import time
import tkinter as tk
from multiprocessing import Process, Manager
from tkinter import filedialog, ttk
from tkinter import messagebox

from util.log import logger


def run_excel_task(file_path, directory_path, progress):
    from excel import Excel
    excel = Excel(file_path, directory_path)

    def update_progress(value):
        progress.value = value

    excel.execute(progress_callback=update_progress)


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


def select_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, directory_path)


def submit():
    file_path = file_entry.get()
    directory_path = dir_entry.get()
    if file_path and directory_path:
        logger.info(f"Excel文件路径: {file_path}")
        logger.info(f"目录路径: {directory_path}")

        # 使用Manager共享进度
        manager = Manager()
        progress = manager.Value('d', 0.0)  # 创建共享进度值

        process = Process(target=run_excel_task, args=(file_path, directory_path, progress))
        process.start()

        while process.is_alive() or progress.value < progressbarOne['maximum']:
            progressbarOne['value'] = progress.value
            root.update()
            time.sleep(1)

        process.join()  # 等待子进程结束
        messagebox.showinfo("完成", "完成")
    else:
        messagebox.showwarning("警告", "请指定Excel文件和目录")


if __name__ == '__main__':
    # 创建主窗口
    root = tk.Tk()
    root.title("ICT收入拆分")

    # 创建并放置控件
    tk.Label(root, text="选择ICT收入文件:").grid(row=0, column=0, padx=10, pady=10)
    file_entry = tk.Entry(root, width=50)
    file_entry.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="浏览", command=select_file).grid(row=0, column=2, padx=10, pady=10)

    tk.Label(root, text="选择自研成本测算目录:").grid(row=1, column=0, padx=10, pady=10)
    dir_entry = tk.Entry(root, width=50)
    dir_entry.grid(row=1, column=1, padx=10, pady=10)
    tk.Button(root, text="浏览", command=select_directory).grid(row=1, column=2, padx=10, pady=10)

    button = tk.Button(root, text="开始分析", command=submit).grid(row=2, column=1, pady=20)

    tk.Label(root, text="分析进度:").grid(row=3, column=0, padx=10, pady=10)
    progressbarOne = ttk.Progressbar(root, length=100, mode='determinate', orient=tk.HORIZONTAL)
    progressbarOne['maximum'] = 100
    progressbarOne['value'] = 0
    progressbarOne.grid(row=3, column=1, padx=10, pady=10)

    # 运行主循环
    root.mainloop()
