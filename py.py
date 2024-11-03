import ffmpeg
import os
import glob
import threading
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
from packaging import version
import subprocess

# Version information
CURRENT_VERSION = "2.0"  # Your app's current version
REPO_API_URL = "https://api.github.com/repos/ArielleirA-source/Nokia-Video-Converter/releases/latest"

def convert_to_webm(input_file):
    base_name = os.path.splitext(input_file)[0]
    webm_file = f"{base_name}.webm"
    ffmpeg.input(input_file).output(webm_file).run(overwrite_output=True)
    return webm_file

def convert_to_flv(input_file):
    base_name = os.path.splitext(input_file)[0]
    flv_file = f"{base_name}.flv"
    ffmpeg.input(input_file).output(
        flv_file,
        vf="scale=320:240",
        qscale=0,
        ar=44100
    ).run(overwrite_output=True)

def process_video(input_file, file_listbox, progress_var, total_files):
    if not input_file.endswith(".webm"):
        input_file = convert_to_webm(input_file)
        file_listbox.insert(ctk.END, f"Converted {os.path.basename(input_file)} to .webm")
    
    convert_to_flv(input_file)
    file_listbox.insert(ctk.END, f"Converted {os.path.basename(input_file)} to .flv")
    
    # Update the progress bar
    progress_var.set(progress_var.get() + 1 / total_files)

def batch_convert(folder_path, file_listbox, progress_bar):
    files = glob.glob(os.path.join(folder_path, "*"))
    total_files = len(files)

    if not files:
        messagebox.showwarning("No Files", "No files found in the selected folder.")
        return

    progress_bar.set(0)  # Reset progress bar
    progress_var = ctk.DoubleVar(value=0)
    for input_file in files:
        process_video(input_file, file_listbox, progress_var, total_files)
        progress_bar.set(progress_var.get())  # Update the progress bar

    messagebox.showinfo("Conversion Complete", "All files have been processed successfully!")

def start_conversion(folder_path, file_listbox, progress_bar):
    threading.Thread(target=batch_convert, args=(folder_path, file_listbox, progress_bar)).start()

def select_folder(file_listbox, progress_bar):
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    file_listbox.delete(0, ctk.END)
    files = glob.glob(os.path.join(folder_path, "*"))

    if not files:
        file_listbox.insert(ctk.END, "No files found.")
    else:
        for file in files:
            file_listbox.insert(ctk.END, os.path.basename(file))

        convert_button.configure(state=ctk.NORMAL)
        convert_button.configure(command=lambda: start_conversion(folder_path, file_listbox, progress_bar))

def check_for_updates():
    try:
        response = requests.get(REPO_API_URL)
        response.raise_for_status()

        latest_release = response.json()
        latest_version = latest_release['tag_name'].strip('v')
        release_url = latest_release['html_url']
        
        if version.parse(latest_version) > version.parse(CURRENT_VERSION):
            update_prompt = messagebox.askyesno("Update Available", 
                                                f"A new version ({latest_version}) is available! "
                                                f"Do you want to download and install it?")
            if update_prompt:
                for asset in latest_release['assets']:
                    if asset['name'] == "Video2NokiaInstaller.exe":
                        download_url = asset['browser_download_url']
                        local_installer_path = os.path.join(os.getcwd(), "Video2NokiaInstaller.exe")
                        
                        # Download the installer file
                        with requests.get(download_url, stream=True) as installer_request:
                            installer_request.raise_for_status()
                            with open(local_installer_path, 'wb') as installer_file:
                                for chunk in installer_request.iter_content(chunk_size=8192):
                                    installer_file.write(chunk)
                        # Run the installer
                        subprocess.run(local_installer_path, shell=True)
                        messagebox.showinfo("Installation", "The new version has been downloaded and launched for installation.")
                        return
                messagebox.showwarning("Installer Not Found", "The installer file could not be found in the latest release.")
        else:
            messagebox.showinfo("No Updates", "You're using the latest version.")
    except requests.RequestException as e:
        messagebox.showerror("Update Check Failed", f"Error checking for updates:\n{e}")

# Initialize CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create the main window
root = ctk.CTk()
root.title("Batch Video Converter")
root.geometry("500x450")

# Label
label = ctk.CTkLabel(root, text="Select a folder with video files to convert:")
label.pack(pady=10)

# Frame for Listbox and Scrollbar
frame = ctk.CTkFrame(root)
frame.pack(pady=10)

# Listbox to display files
file_listbox = Listbox(frame, width=50, height=10, selectmode="single")
file_listbox.pack(side="left", fill="y")

# Scrollbar for the Listbox
scrollbar = Scrollbar(frame, orient="vertical")
scrollbar.config(command=file_listbox.yview)
scrollbar.pack(side="right", fill="y")

file_listbox.config(yscrollcommand=scrollbar.set)

# Select Folder Button
select_button = ctk.CTkButton(root, text="Select Folder", command=lambda: select_folder(file_listbox, progress_bar))
select_button.pack(pady=5)

# Convert Button
convert_button = ctk.CTkButton(root, text="Convert to .flv", state=ctk.DISABLED)
convert_button.pack(pady=5)

# Progress Bar
progress_bar = ctk.CTkProgressBar(root, width=400)
progress_bar.pack(pady=10)
progress_bar.set(0)

# Update Button
update_button = ctk.CTkButton(root, text="Check for Updates", command=check_for_updates)
update_button.pack(pady=5)

# Run the main event loop
root.mainloop()
