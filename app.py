import tkinter as tk
from tkinter import scrolledtext
import time
import psutil
import os
import sys
import subprocess

class NetsupportBypasser:
    def __init__(self, master):
        self.master = master
        master.title("Netsupport Bypasser, bởi Nguyễn Hoàng Long 7a6 (18/3)")

        self.task_to_kill = ["StudentUI.exe", "runplugin.exe", "Runplugin64.exe", "client32.exe","runplugin.exe", "Runplugin64.exe", "client32.exe"]
        self.netsupport_path = r"C:\Program Files (x86)\NetSupport\NetSupport School"  # Đường dẫn tới thư mục Netsupport

        self.kill_button = tk.Button(master, text="Dừng Netsupport", command=self.kill_netsupport_tasks)
        self.kill_button.pack(pady=20)

        self.restore_button = tk.Button(master, text="Khôi phục Netsupport", command=self.restore_netsupport)
        self.restore_button.pack(pady=10)

        self.relaunch_student_ui_button = tk.Button(master, text="Bật lại StudentUI.exe", command=self.relaunch_student_ui)
        self.relaunch_student_ui_button.pack(pady=10)

        self.log_console = scrolledtext.ScrolledText(master, height=15, width=100)
        self.log_console.pack(padx=20, pady=10)
        self.log_console.config(state=tk.DISABLED)  # Make it read-only

        # Tell Tkinter to call the self.on_closing method when the window is closed
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.check_admin_and_initialize()  # check admin and run

    def log(self, message):
        self.log_console.config(state=tk.NORMAL)
        self.log_console.insert(tk.END, f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        self.log_console.see(tk.END)  # Auto-scroll to the bottom
        self.log_console.config(state=tk.DISABLED)

    def is_admin(self):
        """Check if the script is running with administrator privileges."""
        try:
            if os.name == 'nt':  # For Windows
                import ctypes
                # UAC is only on Windows
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:  # For Unix-like systems
                return os.geteuid() == 0
        except Exception as e:
            self.log(f"Lỗi khi kiểm tra quyền admin: {e}")
            return False

    def check_admin_and_initialize(self):
        """Check for admin rights and initialize or show error."""
        if not self.is_admin():
            self.log("Ứng dụng cần được chạy với quyền quản trị viên để có thể tắt Netsupport.")
            self.log("Vui lòng chạy lại ứng dụng với quyền quản trị viên.")
            self.kill_button.config(state=tk.DISABLED)  # Disable the button
            self.restore_button.config(state=tk.DISABLED)  # Disable the restore button
            self.relaunch_student_ui_button.config(state=tk.DISABLED) #disable luôn nút bật lại
        else:
            self.log("Chào mừng đến với Netsupport Bypasser v5.14.25(ALPHA)")
            self.log("Ứng dụng đang chạy với quyền quản trị viên.")

    def kill_process(self, process_name):
        """Cố gắng dừng một tiến trình bằng psutil."""
        killed = False
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    self.log(f"Đã tìm thấy tiến trình với tên: {process_name} (PID: {proc.info['pid']}). Đang cố gắng dừng...")
                    proc.kill()
                    killed = True
                    self.log(f"Đã dừng thành công tiến trình: {process_name} (PID: {proc.info['pid']})")
        except psutil.NoSuchProcess:
            self.log(f"Không tìm thấy tiến trình: {process_name}")
        except psutil.AccessDenied:
            self.log(f"Không có quyền dừng tiến trình: {process_name}. Thử chạy với quyền quản trị viên.")
        except Exception as e:
            self.log(f"Lỗi khi dừng tiến trình {process_name}: {e}")
        return killed

    def kill_netsupport_tasks(self):
        self.log("Bắt đầu kiểm tra và dừng các tác vụ Netsupport...")
        tasks_found = False
        successful_kills = 0
        failed_kills = 0

        for task in self.task_to_kill:
            process_found = False
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'].lower() == task.lower():
                        process_found = True
                        tasks_found = True
                        self.log(f"Đã tìm thấy tác vụ: {task} (PID: {proc.info['pid']}). Đang cố gắng dừng...")
                        try:
                            proc.kill()
                            self.log(f"Đã dừng thành công tác vụ: {task} (PID: {proc.info['pid']})")
                            successful_kills += 1
                        except psutil.NoSuchProcess:
                            self.log(f"Tiến trình {task} (PID: {proc.info['pid']}) không còn tồn tại.")
                        except psutil.AccessDenied:
                            self.log(f"Không có quyền dừng tác vụ: {task} (PID: {proc.info['pid']}). Thử chạy với quyền quản trị viên.")
                            failed_kills += 1
                        except Exception as e:
                            self.log(f"Lỗi khi dừng tác vụ {task} (PID: {proc.info['pid']}): {e}")
                            failed_kills += 1
            except Exception as e:
                self.log(f"Lỗi khi kiểm tra tác vụ {task}: {e}")

            if not process_found:
                self.log(f"Không tìm thấy tác vụ: {task}")

        if not tasks_found:
            self.log("Không phát hiện tác vụ Netsupport nào đang chạy.")
        else:
            self.log("Hoàn tất quá trình dừng tác vụ.")
            self.log(f"Số tác vụ dừng thành công: {successful_kills}")
            self.log(f"Số tác vụ dừng thất bại: {failed_kills}")

    def restore_netsupport(self):
        """Khởi động lại tiến trình client32.exe."""
        client32_path = os.path.join(self.netsupport_path, "client32.exe")
        if os.path.exists(client32_path):
            try:
                subprocess.Popen([client32_path])
                self.log(f"Đã khởi động lại Netsupport Client (client32.exe) từ đường dẫn: {client32_path}")
            except Exception as e:
                self.log(f"Lỗi khi khởi động lại client32.exe: {e}")
        else:
            self.log(f"Không tìm thấy client32.exe tại đường dẫn: {client32_path}")

    def relaunch_student_ui(self):
        """Khởi động lại tiến trình StudentUI.exe."""
        student_ui_path = os.path.join(self.netsupport_path, "StudentUI.exe")
        if os.path.exists(student_ui_path):
            try:
                subprocess.Popen([student_ui_path])
                self.log(f"Đã khởi động lại StudentUI.exe từ đường dẫn: {student_ui_path}")
            except Exception as e:
                self.log(f"Lỗi khi khởi động lại StudentUI.exe: {e}")
        else:
            self.log(f"Không tìm thấy StudentUI.exe tại đường dẫn: {student_ui_path}")
    
    def on_closing(self):
        """Hàm được gọi khi người dùng nhấp vào nút đóng."""
        self.log("Đang đóng ứng dụng...")
        self.master.destroy()  # This will destroy the main window
        self.master.quit()    # This will stop the Tkinter event loop

if __name__ == "__main__":
    root = tk.Tk()
    app = NetsupportBypasser(root)
    root.mainloop()
