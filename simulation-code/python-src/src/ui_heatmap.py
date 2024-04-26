import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

# Mapping of pollutant names to their corresponding script files
pollutant_scripts = {
    'NO2': 'no2_heatmap.py',
    'Ozone': 'ozone_heatmap.py',
    'Pb': 'pb_heatmap.py',
    'PM10': 'pm10_heatmap.py',
    'PM2.5': 'pm25_heatmap.py',
    'SO2': 'so2_heatmap.py',
    'CO': 'co_heatmap.py'
}

def run_heatmap_script(pollutant):
    script_path = f"src/{pollutant_scripts[pollutant]}"
    # Check if the script file exists
    if os.path.exists(script_path):
        try:
            # Run the script using subprocess with the correct arguments
            subprocess.run(["mpiexec", "-np", "4", "python3", script_path], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Execution Error", f"An error occurred: {e}")
    else:
        messagebox.showinfo("File Not Found", f"Script for {pollutant} does not exist at {script_path}")

def on_enter_button_click():
    selected_pollutant = pollutant_var.get()
    if selected_pollutant:
        run_heatmap_script(selected_pollutant)
    else:
        messagebox.showwarning("Selection Missing", "Please select a pollutant from the dropdown.")

# Setup the GUI
root = tk.Tk()
root.title("Pollutant Heatmap Selector")
root.geometry("400x200")  # Width x Height
root.configure(bg="#34495e")

# Set the theme for ttk
style = ttk.Style(root)
style.theme_use("clam")

# Customize Combobox style
style.configure("TCombobox", foreground="#34495e", background="#ecf0f1", fieldbackground="#ecf0f1")
style.map('TCombobox', fieldbackground=[('readonly', '#ecf0f1')])

# Dropdown menu for pollutant selection
pollutant_var = tk.StringVar()
pollutant_dropdown = ttk.Combobox(root, textvariable=pollutant_var, values=list(pollutant_scripts.keys()), state="readonly", width=20)
pollutant_dropdown.grid(column=0, row=0, padx=50, pady=20)
pollutant_dropdown.current(0)  # Set the default value

# Customize Button style
style.configure("TButton", foreground="#2c3e50", background="#2ecc71", font=('Helvetica', 11, 'bold'), borderwidth='1')
style.map("TButton", foreground=[('active', '!disabled', '#2c3e50')], background=[('active', '#27ae60')])

# Button to generate heatmap
enter_button = ttk.Button(root, text="Enter", style='TButton', command=on_enter_button_click)
enter_button.grid(column=0, row=1, padx=10, pady=10, sticky="ew")
enter_button.bind('<Return>', lambda event: on_enter_button_click())

# Center the window on the screen
root.eval('tk::PlaceWindow . center')

root.mainloop()
