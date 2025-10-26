import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import threading

# Determine base directory (for PyInstaller compatibility)
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXE_PATH = os.path.join(BASE_DIR, "build", "Release", "batch_ir2tif.exe")

class ThermalConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Autel Thermal JPG → TIFF Converter")
        self.root.geometry("650x480")
        self.root.resizable(True, True)
        self.conversion_running = False

        # Input folder
        tk.Label(root, text="Input Folder (Autel JPGs):").pack(anchor="w", padx=10, pady=(10, 0))
        self.input_var = tk.StringVar()
        tk.Entry(root, textvariable=self.input_var, width=70).pack(fill="x", padx=10, pady=5)
        tk.Button(root, text="Browse...", command=self.browse_input).pack(anchor="e", padx=10)

        # Output folder
        tk.Label(root, text="Output Folder (TIFFs):").pack(anchor="w", padx=10, pady=(10, 0))
        self.output_var = tk.StringVar()
        tk.Entry(root, textvariable=self.output_var, width=70).pack(fill="x", padx=10, pady=5)
        tk.Button(root, text="Browse...", command=self.browse_output).pack(anchor="e", padx=10)

        # Convert button
        self.convert_btn = tk.Button(root, text="Convert Images", command=self.start_conversion, height=2)
        self.convert_btn.pack(pady=15)

        # Log console with clear button
        log_frame = tk.Frame(root)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        log_header = tk.Frame(log_frame)
        log_header.pack(fill="x")
        tk.Label(log_header, text="Log:").pack(side="left")
        tk.Button(log_header, text="Clear Log", command=self.clear_log).pack(side="right")
        
        self.log = scrolledtext.ScrolledText(log_frame, height=12, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True, pady=(5, 0))

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_var.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_var.set(folder)

    def clear_log(self):
        self.log.config(state="normal")
        self.log.delete(1.0, "end")
        self.log.config(state="disabled")

    def log_message(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")
        self.root.update_idletasks()

    def run_conversion(self, input_dir, output_dir, exe):
        """Run in background thread with real-time output capture"""
        try:
            # Start process with pipes for real-time output
            process = subprocess.Popen(
                [exe, input_dir, output_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                cwd=os.path.dirname(exe),
                universal_newlines=True
            )

            # Read stdout in real-time
            while True:
                output = process.stdout.readline()
                if output:
                    self.root.after(0, lambda msg=output.strip(): self.log_message(msg))
                elif process.poll() is not None:
                    break

            # Get any remaining output
            remaining_stdout, stderr = process.communicate()
            if remaining_stdout:
                for line in remaining_stdout.strip().split('\n'):
                    if line:
                        self.root.after(0, lambda msg=line: self.log_message(msg))

            # Check return code
            if process.returncode == 0:
                self.root.after(0, lambda: self.on_conversion_success())
            else:
                if stderr:
                    self.root.after(0, lambda err=stderr: self.on_conversion_error(err))
                else:
                    self.root.after(0, lambda: self.on_conversion_error("Process failed with no error message"))
                    
        except Exception as e:
            self.root.after(0, lambda: self.on_conversion_exception(str(e)))
        finally:
            self.root.after(0, self.on_conversion_done)

    def on_conversion_success(self):
        self.log_message("\n✅ Conversion completed successfully!")
        messagebox.showinfo("Success", "All images converted!")

    def on_conversion_error(self, stderr):
        self.log_message("\n❌ Conversion failed.")
        if stderr:
            # Log stderr in chunks to avoid overwhelming the log
            lines = stderr.strip().split('\n')
            for line in lines[:50]:  # Limit to first 50 lines
                self.log_message(line)
            if len(lines) > 50:
                self.log_message(f"... ({len(lines) - 50} more error lines)")
        messagebox.showerror("Error", "Conversion failed. Check log for details.")

    def on_conversion_exception(self, msg):
        self.log_message(f"\n💥 Exception: {msg}")
        messagebox.showerror("Error", f"Failed to run converter:\n{msg}")

    def on_conversion_done(self):
        self.conversion_running = False
        self.convert_btn.config(state="normal", text="Convert Images")
        self.log_message("\n" + "="*50 + "\n")

    def start_conversion(self):
        if self.conversion_running:
            return

        input_dir = self.input_var.get().strip()
        output_dir = self.output_var.get().strip()

        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        if not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Input folder does not exist.")
            return

        exe = os.path.abspath(EXE_PATH)
        if not os.path.isfile(exe):
            self.log_message(f"❌ Executable not found: {exe}")
            messagebox.showerror("Error", f"batch_ir2tif.exe not found at:\n{exe}")
            return

        # Start background thread
        self.conversion_running = True
        self.convert_btn.config(state="disabled", text="Converting... (please wait)")
        self.log_message("="*50)
        self.log_message("🚀 Starting conversion...")
        self.log_message(f"📁 Input:  {input_dir}")
        self.log_message(f"📁 Output: {output_dir}")
        self.log_message("="*50 + "\n")

        thread = threading.Thread(
            target=self.run_conversion,
            args=(input_dir, output_dir, exe),
            daemon=True
        )
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ThermalConverterGUI(root)
    root.mainloop()