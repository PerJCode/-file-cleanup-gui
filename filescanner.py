import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import csv
from datetime import datetime, timedelta

class FileScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Envafors Cleanup Tool")
        self.root.geometry("1200x900")
        self.root.configure(bg='white')

        style = ttk.Style()
        style.configure('Main.TFrame', background='white')
        style.configure('Header.TLabel', font=('Segoe UI', 28, 'bold'), background='white', foreground='#2c3e50')
        style.configure('Section.TLabelframe', background='white', font=('Segoe UI', 12))
        style.configure('Section.TLabelframe.Label', font=('Segoe UI', 12, 'bold'), background='white', foreground='#34495e')
        style.configure('Action.TButton', font=('Segoe UI', 12), padding=10)

        container = ttk.Frame(root, padding="30", style='Main.TFrame')
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        header_frame = ttk.Frame(container, style='Main.TFrame')
        header_frame.grid(row=0, column=0, pady=(0, 40))
        header_label = ttk.Label(header_frame, text="📁 Scan for old files", style='Header.TLabel')
        header_label.pack()

        input_frame = ttk.LabelFrame(container, text="Select folder to scan", padding="20", style='Section.TLabelframe')
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        input_frame.grid_columnconfigure(0, weight=1)

        input_container = ttk.Frame(input_frame, style='Main.TFrame')
        input_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        input_container.grid_columnconfigure(0, weight=1)

        self.folder_path = tk.StringVar()
        folder_entry = ttk.Entry(input_container, textvariable=self.folder_path, font=('Segoe UI', 12), width=80)
        folder_entry.grid(row=0, column=0, padx=(0, 10), pady=(0, 10))

        browse_btn = ttk.Button(input_container, text="🗂 Browse", command=self.browse_folder, style='Action.TButton')
        browse_btn.grid(row=0, column=1)

        action_frame = ttk.Frame(container, style='Main.TFrame')
        action_frame.grid(row=2, column=0, pady=(0, 30))

        filter_label = ttk.Label(action_frame, text="File type (e.g. .pdf or .docx):", font=('Segoe UI', 12), background='white')
        filter_label.pack()
        self.filetype_filter = tk.StringVar()
        filter_entry = ttk.Entry(action_frame, textvariable=self.filetype_filter, font=('Segoe UI', 12), width=20)
        filter_entry.pack(pady=(0, 10))

        scan_btn = ttk.Button(action_frame, text="🔍 Scan for old files", command=self.scan_files, style='Action.TButton')
        scan_btn.pack(pady=8)

        export_btn = ttk.Button(action_frame, text="💾 Export to CSV", command=self.export_to_csv, style='Action.TButton')
        export_btn.pack(pady=8)

        delete_btn = ttk.Button(action_frame, text="❌ Delete all listed files", command=self.delete_all_files, style='Action.TButton')
        delete_btn.pack(pady=8)

        sort_label = ttk.Label(action_frame, text="Sort CSV by:", font=('Segoe UI', 12), background='white')
        sort_label.pack(pady=(10, 0))

        self.sort_option = tk.StringVar(value="No sorting")
        sort_dropdown = ttk.Combobox(action_frame, textvariable=self.sort_option, state="readonly", font=('Segoe UI', 12), width=30)
        sort_dropdown['values'] = ["No sorting", "Largest files first", "Oldest files first"]
        sort_dropdown.pack(pady=(0, 10))

        result_frame = ttk.LabelFrame(container, text="Results", padding="20", style='Section.TLabelframe')
        result_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        container.grid_rowconfigure(3, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=('Consolas', 12), background='white', borderwidth=1, relief="solid")
        self.result_text.pack(expand=True, fill='both')

        self.summary_label = ttk.Label(container, text="", font=('Segoe UI', 12, 'bold'), foreground='#27ae60', background='white')
        self.summary_label.grid(row=4, column=0, sticky='w', pady=(10, 10))

        self.footer_label = ttk.Label(
            container,
            text="Developed by Per Roel Jørgensen for Envafors – 2025",
            font=('Segoe UI', 11, 'italic'),
            background='white',
            foreground='#7f8c8d'
        )
        self.footer_label.grid(row=5, column=0, sticky='w', pady=(0, 10))

        self.result_text.tag_configure('filename', font=('Consolas', 12, 'bold'), foreground='#2980b9')
        self.result_text.tag_configure('header', font=('Consolas', 12, 'bold'), foreground='#2c3e50')
        self.result_text.tag_configure('success', font=('Consolas', 12, 'bold'), foreground='#27ae60')
        self.result_text.tag_configure('error', foreground='#c0392b')
        self.result_text.tag_configure('separator', foreground='#bdc3c7')

        self.found_files = []

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def get_file_size_formatted(self, size_in_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.1f} TB"

    def scan_files(self):
        self.found_files = []
        folder_path = self.folder_path.get()
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Error: Please select a valid folder!", 'error')
            self.summary_label.config(text="")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "📂 Scanning folder: ", 'header')
        self.result_text.insert(tk.END, f"{folder_path}\n")
        self.result_text.insert(tk.END, "─" * 100 + "\n\n", 'separator')

        now = datetime.now()
        threshold_date = now - timedelta(days=90)

        for root_dir, dirs, files in os.walk(folder_path):
            for file in files:
                if self.filetype_filter.get():
                    if not file.lower().endswith(self.filetype_filter.get().lower()):
                        continue

                file_path = os.path.join(root_dir, file)
                try:
                    stats = os.stat(file_path)
                    modified_time = datetime.fromtimestamp(stats.st_mtime)
                    if modified_time < threshold_date:
                        relative_path = os.path.relpath(file_path, folder_path)
                        size = self.get_file_size_formatted(stats.st_size)
                        date_str = modified_time.strftime("%d-%m-%Y %H:%M")

                        self.result_text.insert(tk.END, "📄 ", 'header')
                        self.result_text.insert(tk.END, f"{relative_path}\n", 'filename')
                        self.result_text.insert(tk.END, f"   Size: {size}\n")
                        self.result_text.insert(tk.END, f"   Last modified: {date_str}\n")
                        self.result_text.insert(tk.END, "─" * 100 + "\n\n", 'separator')

                        self.found_files.append([file_path, stats.st_size, modified_time])

                except Exception as e:
                    self.result_text.insert(tk.END, f"Error reading {file_path}: {e}\n", 'error')
                    self.result_text.insert(tk.END, "─" * 100 + "\n\n", 'separator')

                self.root.update_idletasks()

        if self.found_files:
            total_size = sum([int(r[1]) for r in self.found_files])
            display_size = self.get_file_size_formatted(total_size)
            file_count = len(self.found_files)
            self.summary_label.config(
                text=f"📄 Files found: {file_count}    🧲 Total space: {display_size}"
            )
        else:
            self.result_text.insert(tk.END, "✓ No files older than 90 days found.\n", 'success')
            self.summary_label.config(text="")

    def export_to_csv(self):
        if not self.found_files:
            self.result_text.insert(tk.END, "\nNo data to export.\n", 'error')
            return

        sort_choice = self.sort_option.get()
        sorted_files = self.found_files.copy()

        if sort_choice == "Largest files first":
            sorted_files.sort(key=lambda x: x[1], reverse=True)
        elif sort_choice == "Oldest files first":
            sorted_files.sort(key=lambda x: x[2])

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            try:
                with open(save_path, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(["File path", "Size (bytes)", "Last modified"])
                    for path, size, date in sorted_files:
                        writer.writerow([path, size, date.strftime("%d-%m-%Y %H:%M")])
                self.result_text.insert(tk.END, f"✓ Exported to: {save_path}\n", 'success')
            except Exception as e:
                self.result_text.insert(tk.END, f"Export error: {e}\n", 'error')

    def delete_all_files(self):
        if not self.found_files:
            messagebox.showinfo("No files", "There are no files to delete.")
            return

        confirm = messagebox.askyesno("Confirm deletion", "Are you sure you want to delete all listed files?")
        if not confirm:
            return

        errors = 0
        for file_data in self.found_files:
            file_path = file_data[0]
            try:
                os.remove(file_path)
            except Exception as e:
                errors += 1
                self.result_text.insert(tk.END, f"Error deleting {file_path}: {e}\n", 'error')

        if errors == 0:
            messagebox.showinfo("Deletion complete", "All listed files have been deleted.")
        else:
            messagebox.showwarning("Partial deletion", f"{errors} files could not be deleted.")

        self.scan_files()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileScannerGUI(root)
    root.mainloop()
