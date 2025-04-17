import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import document_analyzer as doc_analyzer

class RedirectText:
    """Class for redirecting stdout to a tkinter Text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Auto-scroll to the bottom
        self.text_widget.configure(state=tk.DISABLED)
    
    def flush(self):
        pass

class DocumentAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Content Analyzer")
        self.root.geometry("850x700")
        self.root.minsize(750, 600)
        
        # Create a main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)  # Status area will expand
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.language = tk.StringVar(value="arabic")
        self.output_format = tk.StringVar(value="text")
        self.extract_mode = tk.StringVar(value="full")
        self.model_name = tk.StringVar(value="gemini-2.0-flash")
        self.processing = False
        
        # Input File Selection
        ttk.Label(main_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        input_entry = ttk.Entry(main_frame, textvariable=self.input_path, width=50)
        input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output Path
        ttk.Label(main_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Language Selection
        ttk.Label(main_frame, text="Language:").grid(row=2, column=0, sticky=tk.W, pady=5)
        language_frame = ttk.Frame(main_frame)
        language_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(language_frame, text="Arabic", variable=self.language, value="arabic").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(language_frame, text="English", variable=self.language, value="english").pack(side=tk.LEFT, padx=5)
        
        # Output Format Selection
        ttk.Label(main_frame, text="Output Format:").grid(row=3, column=0, sticky=tk.W, pady=5)
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(format_frame, text="Text File (.txt)", variable=self.output_format, value="text", 
                        command=self.update_output_extension).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="Word Document (.docx)", variable=self.output_format, value="docx", 
                        command=self.update_output_extension).pack(side=tk.LEFT, padx=5)
        
        # Extraction Mode Selection
        ttk.Label(main_frame, text="Extraction Mode:").grid(row=4, column=0, sticky=tk.W, pady=5)
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="Full Text", variable=self.extract_mode, value="full").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Summary", variable=self.extract_mode, value="summary").pack(side=tk.LEFT, padx=5)
        
        # Model Selection
        ttk.Label(main_frame, text="Gemini Model:").grid(row=5, column=0, sticky=tk.W, pady=5)
        models = [
            "gemini-1.5-pro-latest", 
            "gemini-1.5-pro-001",
            "gemini-1.5-flash-latest", 
            "gemini-1.5-flash-001",
            "gemini-2.0-pro",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite"
        ]
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_name, values=models, width=30)
        model_combo.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Analyze Button
        self.analyze_button = ttk.Button(main_frame, text="Analyze Document", command=self.start_analysis)
        self.analyze_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Status Area
        ttk.Label(main_frame, text="Status:").grid(row=8, column=0, sticky=tk.NW, pady=5)
        self.status_area = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        self.status_area.grid(row=8, column=1, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)
        self.status_area.configure(state=tk.DISABLED)
        
        # Redirect stdout to the status area
        self.old_stdout = sys.stdout
        self.text_redirect = RedirectText(self.status_area)
        
        # Footer with additional buttons
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=9, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(footer_frame, text="Open Output File", command=self.open_output_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(footer_frame, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT, padx=5)
        
    def browse_input(self):
        """Open file dialog to select input file (PDF or image)"""
        filename = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[
                ("Document Files", "*.pdf *.jpg *.jpeg *.png *.tiff *.bmp"), 
                ("PDF Files", "*.pdf"),
                ("Image Files", "*.jpg *.jpeg *.png *.tiff *.bmp"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.input_path.set(filename)
            # Set default output path based on input file
            self.update_default_output_path(filename)
    
    def update_default_output_path(self, input_filename):
        """Update default output path based on input file and selected options"""
        base_filename = os.path.splitext(os.path.basename(input_filename))[0]
        mode = self.extract_mode.get()
        lang = self.language.get()
        ext = ".docx" if self.output_format.get() == "docx" else ".txt"
        output_dir = os.path.dirname(input_filename)
        
        self.output_path.set(f"{output_dir}/{base_filename}_{mode}_{lang}{ext}")
    
    def update_output_extension(self):
        """Update output file extension when format changes"""
        if self.input_path.get():
            self.update_default_output_path(self.input_path.get())
    
    def browse_output(self):
        """Open file dialog to set output location"""
        default_ext = ".docx" if self.output_format.get() == "docx" else ".txt"
        filetypes = [("Word Documents", "*.docx"), ("All Files", "*.*")] if self.output_format.get() == "docx" else [("Text Files", "*.txt"), ("All Files", "*.*")]
        
        filename = filedialog.asksaveasfilename(
            title="Save Output File",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        if filename:
            self.output_path.set(filename)
    
    def start_analysis(self):
        """Start the document analysis process in a separate thread"""
        # Validate inputs
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
            
        # Update default output path if needed
        if self.input_path.get() and not self.output_path.get():
            self.update_default_output_path(self.input_path.get())
        
        # Disable controls during processing
        self.processing = True
        self.analyze_button.config(state=tk.DISABLED)
        self.progress.start(10)
        
        # Clear status area
        self.status_area.configure(state=tk.NORMAL)
        self.status_area.delete(1.0, tk.END)
        self.status_area.configure(state=tk.DISABLED)
        
        # Redirect stdout to status area
        sys.stdout = self.text_redirect
        
        # Set the model name
        doc_analyzer.GEMINI_MODEL_NAME = self.model_name.get()
        print(f"[*] Using Gemini model: {doc_analyzer.GEMINI_MODEL_NAME}")
        
        # Start analysis in a separate thread
        thread = threading.Thread(target=self.analyze_document)
        thread.daemon = True
        thread.start()
    
    def analyze_document(self):
        """Analyze the document in a separate thread"""
        try:
            # Upload the file
            uploaded_file = doc_analyzer.upload_file_to_gemini(self.input_path.get())
            
            if uploaded_file:
                # Extract content
                extracted_text, summary_text = doc_analyzer.analyze_document(
                    uploaded_file, 
                    self.extract_mode.get(), 
                    self.language.get()
                )
                
                # Determine which content to save
                content_to_save = summary_text if self.extract_mode.get() == "summary" and summary_text else extracted_text
                
                # Save content
                if content_to_save and self.output_path.get():
                    if self.output_format.get() == "docx":
                        base_filename = os.path.splitext(os.path.basename(self.input_path.get()))[0]
                        title = f"{'Summary' if self.extract_mode.get() == 'summary' else 'Extracted Text'} - {base_filename}"
                        success = doc_analyzer.save_to_word_file(
                            content_to_save, 
                            self.output_path.get(), 
                            title,
                            self.language.get()
                        )
                    else:
                        success = doc_analyzer.save_to_text_file(
                            content_to_save, 
                            self.output_path.get()
                        )
                    
                    if success:
                        print(f"\n[+] Content saved to: {self.output_path.get()}")
                    else:
                        print("\n[!] Failed to save content.")
                else:
                    print("\n[!] No content to save. Extraction failed.")
            else:
                print("\n[!] Process failed: Could not upload or process the file.")
        
        except Exception as e:
            print(f"[!] An error occurred: {e}")
        
        finally:
            # Reset the UI on the main thread
            self.root.after(0, self.finalize_analysis)
    
    def finalize_analysis(self):
        """Reset the UI after analysis is complete"""
        # Restore stdout
        sys.stdout = self.old_stdout
        
        # Enable controls
        self.processing = False
        self.analyze_button.config(state=tk.NORMAL)
        self.progress.stop()
        
        # Notify completion
        print("[*] Analysis complete.")
        messagebox.showinfo("Complete", "Document analysis has finished!")
    
    def open_output_file(self):
        """Open the output file if it exists"""
        if self.output_path.get() and os.path.exists(self.output_path.get()):
            try:
                os.startfile(self.output_path.get())  # Windows-specific
            except AttributeError:
                # For non-Windows systems
                import subprocess
                subprocess.call(["xdg-open", self.output_path.get()])  # Linux
        else:
            messagebox.showinfo("Info", "No output file available to open.")
    
    def clear_all(self):
        """Clear all input fields"""
        self.input_path.set("")
        self.output_path.set("")
        self.language.set("arabic")
        self.output_format.set("text")
        self.extract_mode.set("full")
        
        # Clear status area
        self.status_area.configure(state=tk.NORMAL)
        self.status_area.delete(1.0, tk.END)
        self.status_area.configure(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentAnalyzerGUI(root)
    root.mainloop()
