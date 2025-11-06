"""
Remote Execute - A beautiful dark-themed remote execution application
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from typing import List, Optional
from database import CredentialDatabase
from remote_executor import LinuxExecutor, WindowsExecutor
import json

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ScriptEditorWindow(ctk.CTkToplevel):
    """Flyout window for creating scripts on the fly"""

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Script Editor")
        self.geometry("800x600")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top frame for filename and script type
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_frame, text="Filename:").grid(row=0, column=0, padx=5, pady=5)
        self.filename_entry = ctk.CTkEntry(top_frame, placeholder_text="script.py")
        self.filename_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(top_frame, text="Type:").grid(row=0, column=2, padx=5, pady=5)
        self.script_type = ctk.CTkComboBox(
            top_frame,
            values=["Python (.py)", "PowerShell (.ps1)", "Bash (.sh)", "Batch (.bat)"],
            width=150
        )
        self.script_type.grid(row=0, column=3, padx=5, pady=5)
        self.script_type.set("Python (.py)")

        # Text editor
        self.text_editor = ctk.CTkTextbox(self, wrap="none", font=("Consolas", 12))
        self.text_editor.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Button frame
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="Save and Use",
            command=self.save_and_use,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(side="left", padx=5)

        # Template button
        ctk.CTkButton(
            button_frame,
            text="Load Template",
            command=self.load_template,
            fg_color="#6c757d",
            hover_color="#5a6268"
        ).pack(side="right", padx=5)

        # Bind script type change to update filename
        self.script_type.configure(command=self.update_filename_extension)

    def update_filename_extension(self, choice):
        """Update filename extension based on script type"""
        current = self.filename_entry.get()
        if current:
            base = os.path.splitext(current)[0]
            ext_map = {
                "Python (.py)": ".py",
                "PowerShell (.ps1)": ".ps1",
                "Bash (.sh)": ".sh",
                "Batch (.bat)": ".bat"
            }
            new_ext = ext_map.get(choice, ".py")
            self.filename_entry.delete(0, "end")
            self.filename_entry.insert(0, f"{base}{new_ext}")

    def load_template(self):
        """Load a template script"""
        script_type = self.script_type.get()
        templates = {
            "Python (.py)": '''#!/usr/bin/env python3
"""
Script description
"""
import sys
import os

def main():
    print("Hello from Python!")
    # Your code here

if __name__ == "__main__":
    main()
''',
            "PowerShell (.ps1)": '''# PowerShell Script
# Description

Write-Host "Hello from PowerShell!"

# Your code here
''',
            "Bash (.sh)": '''#!/bin/bash
# Bash Script
# Description

echo "Hello from Bash!"

# Your code here
''',
            "Batch (.bat)": '''@echo off
REM Batch Script
REM Description

echo Hello from Batch!

REM Your code here
'''
        }

        template = templates.get(script_type, "")
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", template)

    def save_and_use(self):
        """Save the script and pass it back to the main window"""
        filename = self.filename_entry.get().strip()
        if not filename:
            messagebox.showerror("Error", "Please enter a filename")
            return

        content = self.text_editor.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showerror("Error", "Script content is empty")
            return

        # Save to temp file
        temp_dir = os.path.join(os.getcwd(), "temp_scripts")
        os.makedirs(temp_dir, exist_ok=True)

        script_path = os.path.join(temp_dir, filename)
        with open(script_path, 'w') as f:
            f.write(content)

        self.callback(script_path)
        self.destroy()


class CredentialManagerWindow(ctk.CTkToplevel):
    """Window for managing credentials"""

    def __init__(self, parent, db: CredentialDatabase):
        super().__init__(parent)
        self.db = db
        self.title("Credential Manager")
        self.geometry("900x600")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Top button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="Add Credential",
            command=self.add_credential,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Edit Selected",
            command=self.edit_credential,
            fg_color="#ffc107",
            hover_color="#e0a800"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Delete Selected",
            command=self.delete_credential,
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self.refresh_list,
            fg_color="#17a2b8",
            hover_color="#138496"
        ).pack(side="left", padx=5)

        # Credentials list
        self.cred_textbox = ctk.CTkTextbox(main_frame, font=("Consolas", 11))
        self.cred_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.refresh_list()

    def refresh_list(self):
        """Refresh the credentials list"""
        self.cred_textbox.delete("1.0", "end")
        credentials = self.db.get_all_credentials()

        if not credentials:
            self.cred_textbox.insert("1.0", "No credentials stored.\n")
            return

        header = f"{'ID':<5} {'Host':<25} {'Type':<15} {'Username':<20} {'Domain':<15} {'Description':<30}\n"
        self.cred_textbox.insert("end", header)
        self.cred_textbox.insert("end", "=" * 120 + "\n")

        for cred in credentials:
            line = f"{cred['id']:<5} {cred['host']:<25} {cred['credential_type']:<15} {cred['username'] or 'N/A':<20} {cred['domain'] or 'N/A':<15} {cred['description'] or '':<30}\n"
            self.cred_textbox.insert("end", line)

    def add_credential(self):
        """Open dialog to add new credential"""
        dialog = CredentialDialog(self, self.db, None)
        self.wait_window(dialog)
        self.refresh_list()

    def edit_credential(self):
        """Edit selected credential"""
        # Get selected line
        try:
            selection = self.cred_textbox.get("insert linestart", "insert lineend")
            if not selection or selection.startswith("ID") or selection.startswith("=") or "No credentials" in selection:
                messagebox.showwarning("Warning", "Please select a credential to edit")
                return

            cred_id = int(selection.split()[0])
            credential = self.db.get_credential(cred_id)

            if credential:
                dialog = CredentialDialog(self, self.db, credential)
                self.wait_window(dialog)
                self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit credential: {str(e)}")

    def delete_credential(self):
        """Delete selected credential"""
        try:
            selection = self.cred_textbox.get("insert linestart", "insert lineend")
            if not selection or selection.startswith("ID") or selection.startswith("=") or "No credentials" in selection:
                messagebox.showwarning("Warning", "Please select a credential to delete")
                return

            cred_id = int(selection.split()[0])

            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this credential?"):
                self.db.delete_credential(cred_id)
                self.refresh_list()
                messagebox.showinfo("Success", "Credential deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete credential: {str(e)}")


class CredentialDialog(ctk.CTkToplevel):
    """Dialog for adding/editing credentials"""

    def __init__(self, parent, db: CredentialDatabase, credential: Optional[dict] = None):
        super().__init__(parent)
        self.db = db
        self.credential = credential
        self.title("Edit Credential" if credential else "Add Credential")
        self.geometry("500x550")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)

        row = 0

        # Host
        ctk.CTkLabel(main_frame, text="Host/IP:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.host_entry = ctk.CTkEntry(main_frame, placeholder_text="192.168.1.100 or hostname")
        self.host_entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        row += 1

        # Credential Type
        ctk.CTkLabel(main_frame, text="Type:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.type_combo = ctk.CTkComboBox(
            main_frame,
            values=["Windows Local", "Windows Domain", "Linux", "SNMPv2"],
            command=self.on_type_change
        )
        self.type_combo.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        row += 1

        # Username
        ctk.CTkLabel(main_frame, text="Username:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = ctk.CTkEntry(main_frame, placeholder_text="username")
        self.username_entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        self.username_label = ctk.CTkLabel(main_frame, text="Username:")
        row += 1

        # Password
        ctk.CTkLabel(main_frame, text="Password:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(main_frame, placeholder_text="password", show="*")
        self.password_entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        self.password_label = ctk.CTkLabel(main_frame, text="Password:")
        row += 1

        # Domain (Windows only)
        self.domain_label = ctk.CTkLabel(main_frame, text="Domain:")
        self.domain_entry = ctk.CTkEntry(main_frame, placeholder_text="DOMAIN (optional)")
        row += 1

        # Community String (SNMP only)
        self.community_label = ctk.CTkLabel(main_frame, text="Community String:")
        self.community_entry = ctk.CTkEntry(main_frame, placeholder_text="public")
        row += 1

        # Description
        ctk.CTkLabel(main_frame, text="Description:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.description_entry = ctk.CTkEntry(main_frame, placeholder_text="Optional description")
        self.description_entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        row += 1

        # Button frame
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(side="left", padx=5)

        # Load existing data if editing
        if credential:
            self.host_entry.insert(0, credential['host'])
            self.type_combo.set(credential['credential_type'])
            if credential['username']:
                self.username_entry.insert(0, credential['username'])
            if credential['password']:
                self.password_entry.insert(0, credential['password'])
            if credential['domain']:
                self.domain_entry.insert(0, credential['domain'])
            if credential['community_string']:
                self.community_entry.insert(0, credential['community_string'])
            if credential['description']:
                self.description_entry.insert(0, credential['description'])

        # Trigger type change to show/hide fields
        self.on_type_change(self.type_combo.get())

    def on_type_change(self, choice):
        """Handle credential type change"""
        # Hide all optional fields first
        self.domain_label.grid_remove()
        self.domain_entry.grid_remove()
        self.community_label.grid_remove()
        self.community_entry.grid_remove()

        # Show relevant fields
        if choice == "Windows Domain":
            self.domain_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
            self.domain_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        elif choice == "SNMPv2":
            self.community_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
            self.community_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

    def save(self):
        """Save the credential"""
        host = self.host_entry.get().strip()
        if not host:
            messagebox.showerror("Error", "Host/IP is required")
            return

        cred_type = self.type_combo.get()
        username = self.username_entry.get().strip() or None
        password = self.password_entry.get().strip() or None
        domain = self.domain_entry.get().strip() or None
        community = self.community_entry.get().strip() or None
        description = self.description_entry.get().strip() or None

        try:
            if self.credential:
                # Update existing
                self.db.update_credential(
                    self.credential['id'],
                    host=host,
                    credential_type=cred_type,
                    username=username,
                    password=password,
                    domain=domain,
                    community_string=community,
                    description=description
                )
            else:
                # Add new
                self.db.add_credential(
                    host=host,
                    credential_type=cred_type,
                    username=username,
                    password=password,
                    domain=domain,
                    community_string=community,
                    description=description
                )

            messagebox.showinfo("Success", "Credential saved successfully")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credential: {str(e)}")


class RemoteExecuteApp(ctk.CTk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.title("Remote Execute - Dark Edition")
        self.geometry("1200x800")

        # Initialize database
        self.db = CredentialDatabase()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Selected files
        self.selected_files: List[str] = []

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Create the user interface"""

        # Top frame for connection settings
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)

        # Host input
        ctk.CTkLabel(top_frame, text="Host/IP:", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.host_entry = ctk.CTkEntry(
            top_frame,
            placeholder_text="192.168.1.100 or hostname",
            width=300,
            font=("Arial", 12)
        )
        self.host_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Credential selection
        ctk.CTkLabel(top_frame, text="Credentials:", font=("Arial", 14, "bold")).grid(
            row=0, column=2, padx=10, pady=10, sticky="w"
        )
        self.credential_combo = ctk.CTkComboBox(
            top_frame,
            values=["Load credentials..."],
            width=250,
            font=("Arial", 12)
        )
        self.credential_combo.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        # Manage credentials button
        ctk.CTkButton(
            top_frame,
            text="Manage Credentials",
            command=self.open_credential_manager,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=150
        ).grid(row=0, column=4, padx=10, pady=10)

        # Refresh credentials button
        ctk.CTkButton(
            top_frame,
            text="🔄",
            command=self.refresh_credentials,
            width=40,
            fg_color="#17a2b8",
            hover_color="#138496"
        ).grid(row=0, column=5, padx=5, pady=10)

        # Test connection button
        ctk.CTkButton(
            top_frame,
            text="Test Connection",
            command=self.test_connection,
            fg_color="#ffc107",
            hover_color="#e0a800",
            width=150
        ).grid(row=0, column=6, padx=10, pady=10)

        # Middle frame for file selection and execution
        middle_frame = ctk.CTkFrame(self)
        middle_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_rowconfigure(1, weight=1)

        # File selection frame
        file_frame = ctk.CTkFrame(middle_frame)
        file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(file_frame, text="Scripts/Binaries:", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        self.files_entry = ctk.CTkEntry(
            file_frame,
            placeholder_text="No files selected",
            state="readonly",
            font=("Arial", 11)
        )
        self.files_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(
            file_frame,
            text="Browse Files",
            command=self.browse_files,
            fg_color="#007bff",
            hover_color="#0056b3",
            width=120
        ).grid(row=0, column=2, padx=5, pady=10)

        ctk.CTkButton(
            file_frame,
            text="Clear",
            command=self.clear_files,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=80
        ).grid(row=0, column=3, padx=5, pady=10)

        ctk.CTkButton(
            file_frame,
            text="Create New Script",
            command=self.open_script_editor,
            fg_color="#28a745",
            hover_color="#218838",
            width=150
        ).grid(row=0, column=4, padx=5, pady=10)

        # Output textbox
        output_label_frame = ctk.CTkFrame(middle_frame)
        output_label_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")

        ctk.CTkLabel(
            output_label_frame,
            text="Execution Output:",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            output_label_frame,
            text="Clear Output",
            command=self.clear_output,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=100
        ).pack(side="right", padx=10)

        self.output_textbox = ctk.CTkTextbox(
            middle_frame,
            wrap="word",
            font=("Consolas", 11),
            fg_color="#1a1a1a"
        )
        self.output_textbox.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        middle_frame.grid_rowconfigure(2, weight=1)

        # Bottom frame for execution button
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            bottom_frame,
            text="▶ EXECUTE",
            command=self.execute_remote,
            font=("Arial", 16, "bold"),
            height=50,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(fill="x", padx=10, pady=10)

        # Load initial credentials
        self.refresh_credentials()

    def refresh_credentials(self):
        """Refresh the credentials dropdown"""
        credentials = self.db.get_all_credentials()
        if credentials:
            values = [f"{c['id']}: {c['host']} ({c['credential_type']})" for c in credentials]
            self.credential_combo.configure(values=values)
            if values:
                self.credential_combo.set(values[0])
        else:
            self.credential_combo.configure(values=["No credentials stored"])
            self.credential_combo.set("No credentials stored")

    def open_credential_manager(self):
        """Open the credential manager window"""
        CredentialManagerWindow(self, self.db)

    def browse_files(self):
        """Browse for files to execute"""
        files = filedialog.askopenfilenames(
            title="Select Scripts/Binaries",
            filetypes=[
                ("All Files", "*.*"),
                ("Python Scripts", "*.py"),
                ("PowerShell Scripts", "*.ps1"),
                ("Bash Scripts", "*.sh"),
                ("Batch Files", "*.bat"),
                ("Executables", "*.exe")
            ]
        )

        if files:
            self.selected_files.extend(files)
            self.update_files_display()

    def clear_files(self):
        """Clear selected files"""
        self.selected_files = []
        self.update_files_display()

    def update_files_display(self):
        """Update the files display"""
        self.files_entry.configure(state="normal")
        self.files_entry.delete(0, "end")

        if self.selected_files:
            display_text = f"{len(self.selected_files)} file(s) selected: {', '.join([os.path.basename(f) for f in self.selected_files])}"
            self.files_entry.insert(0, display_text)
        else:
            self.files_entry.insert(0, "No files selected")

        self.files_entry.configure(state="readonly")

    def open_script_editor(self):
        """Open the script editor window"""
        def on_script_created(script_path):
            self.selected_files.append(script_path)
            self.update_files_display()
            self.log_output(f"✓ Script created: {script_path}\n", "success")

        ScriptEditorWindow(self, on_script_created)

    def clear_output(self):
        """Clear the output textbox"""
        self.output_textbox.delete("1.0", "end")

    def log_output(self, message: str, level: str = "info"):
        """Log a message to the output textbox"""
        self.output_textbox.insert("end", message)
        self.output_textbox.see("end")

    def test_connection(self):
        """Test connection to the target host"""
        host = self.host_entry.get().strip()
        if not host:
            messagebox.showerror("Error", "Please enter a host/IP address")
            return

        self.log_output(f"Testing connection to {host}...\n", "info")

        def test():
            # Try SSH first
            from remote_executor import RemoteExecutor
            success, message = RemoteExecutor.test_connection(host, 22)
            if success:
                self.log_output(f"✓ SSH (port 22): {message}\n", "success")
            else:
                self.log_output(f"✗ SSH (port 22): {message}\n", "error")

            # Try WinRM
            success, message = RemoteExecutor.test_connection(host, 5985)
            if success:
                self.log_output(f"✓ WinRM (port 5985): {message}\n", "success")
            else:
                self.log_output(f"✗ WinRM (port 5985): {message}\n", "error")

        thread = threading.Thread(target=test, daemon=True)
        thread.start()

    def execute_remote(self):
        """Execute scripts on the remote host"""
        host = self.host_entry.get().strip()
        if not host:
            messagebox.showerror("Error", "Please enter a host/IP address")
            return

        if not self.selected_files:
            messagebox.showerror("Error", "Please select at least one file to execute")
            return

        cred_selection = self.credential_combo.get()
        if cred_selection == "No credentials stored" or cred_selection == "Load credentials...":
            messagebox.showerror("Error", "Please select or create credentials")
            return

        # Extract credential ID
        try:
            cred_id = int(cred_selection.split(":")[0])
            credential = self.db.get_credential(cred_id)

            if not credential:
                messagebox.showerror("Error", "Selected credential not found")
                return

            # Execute in background thread
            thread = threading.Thread(
                target=self.execute_in_background,
                args=(host, credential, self.selected_files[:]),
                daemon=True
            )
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute: {str(e)}")

    def execute_in_background(self, host: str, credential: dict, files: List[str]):
        """Execute files in background thread"""
        try:
            self.log_output(f"\n{'='*80}\n")
            self.log_output(f"Starting remote execution on {host}\n")
            self.log_output(f"Credential Type: {credential['credential_type']}\n")
            self.log_output(f"Files to execute: {len(files)}\n")
            self.log_output(f"{'='*80}\n\n")

            # Determine executor type
            cred_type = credential['credential_type']

            if cred_type in ["Windows Local", "Windows Domain"]:
                executor = WindowsExecutor(
                    host=host,
                    username=credential['username'],
                    password=credential['password'],
                    domain=credential.get('domain')
                )
            elif cred_type == "Linux":
                executor = LinuxExecutor(
                    host=host,
                    username=credential['username'],
                    password=credential['password']
                )
            else:
                self.log_output(f"✗ Unsupported credential type: {cred_type}\n")
                return

            # Connect
            self.log_output("Connecting...\n")
            success, message = executor.connect()

            if not success:
                self.log_output(f"✗ Connection failed: {message}\n")
                self.db.add_execution_history(host, cred_type, "Connection", "Failed", message)
                return

            self.log_output(f"✓ {message}\n\n")

            # Upload files if multiple
            if len(files) > 1:
                self.log_output(f"Uploading {len(files)} files...\n")
                success, message, uploaded_paths = executor.upload_files(files)

                if not success:
                    self.log_output(f"✗ Upload failed: {message}\n")
                    executor.disconnect()
                    return

                self.log_output(f"✓ {message}\n\n")

            # Execute each file
            for file_path in files:
                filename = os.path.basename(file_path)
                self.log_output(f"Executing: {filename}\n")
                self.log_output(f"{'-'*80}\n")

                success, output, error = executor.execute_script(file_path)

                if success:
                    self.log_output(f"✓ Execution successful\n\n")
                    if output:
                        self.log_output(f"Output:\n{output}\n")
                    if error:
                        self.log_output(f"Warnings:\n{error}\n")

                    self.db.add_execution_history(host, cred_type, filename, "Success", output)
                else:
                    self.log_output(f"✗ Execution failed\n\n")
                    if output:
                        self.log_output(f"Output:\n{output}\n")
                    if error:
                        self.log_output(f"Error:\n{error}\n")

                    self.db.add_execution_history(host, cred_type, filename, "Failed", error)

                self.log_output(f"{'-'*80}\n\n")

            # Disconnect
            executor.disconnect()
            self.log_output(f"✓ Disconnected from {host}\n")
            self.log_output(f"{'='*80}\n")

        except Exception as e:
            self.log_output(f"✗ Unexpected error: {str(e)}\n")


def main():
    """Main entry point"""
    app = RemoteExecuteApp()
    app.mainloop()


if __name__ == "__main__":
    main()
