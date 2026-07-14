"""
gui_app.py
----------
PySide6 (Qt) desktop application for frequency table generation.
This replaces the Flask web interface with a native desktop UI.
"""
import sys
import shutil
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QTableWidget,
    QTableWidgetItem, QRadioButton, QButtonGroup, QCheckBox, QSpinBox,
    QComboBox, QLineEdit, QTextEdit, QGroupBox, QProgressDialog,
    QHeaderView, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon

import core


class ProcessingThread(QThread):
    """Background thread for processing the frequency tables."""
    progress = Signal(int, int, str)  # current, total, varname
    finished = Signal(dict)  # result dict
    error = Signal(str)  # error message
    
    def __init__(self, dta_path, output_path, dataset_name, weight_var, weight_value, options):
        super().__init__()
        self.dta_path = dta_path
        self.output_path = output_path
        self.dataset_name = dataset_name
        self.weight_var = weight_var
        self.weight_value = weight_value
        self.options = options
    
    def run(self):
        try:
            result = core.run_full_pipeline(
                dta_path=self.dta_path,
                output_path=self.output_path,
                dataset_name=self.dataset_name,
                weight_var=self.weight_var,
                weight_value=self.weight_value,
                options=self.options,
                progress_callback=self._progress_callback
            )
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))
    
    def _progress_callback(self, done, total, varname):
        self.progress.emit(done, total, varname)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frequency Table Generator")
        self.setMinimumSize(900, 700)
        
        # Data storage
        self.dta_path = None
        self.df = None
        self.meta = None
        self.output_path = None
        self.variable_overview = []
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        
        # Title
        title = QLabel("Frequency Table Generator for Stata Files")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Stack of pages
        self.page_upload = self._create_upload_page()
        self.page_options = self._create_options_page()
        self.page_result = self._create_result_page()
        
        main_layout.addWidget(self.page_upload)
        main_layout.addWidget(self.page_options)
        main_layout.addWidget(self.page_result)
        
        # Initially show only upload page
        self._show_page("upload")
    
    def _show_page(self, page_name):
        """Show only the specified page."""
        self.page_upload.setVisible(page_name == "upload")
        self.page_options.setVisible(page_name == "options")
        self.page_result.setVisible(page_name == "result")
    
    def _create_upload_page(self):
        """Create the upload/step 1 page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Instructions
        info_label = QLabel(
            "<h3>Step 1 — Upload your Stata dataset</h3>"
            "<p>Select a <code>.dta</code> file. We'll show you every variable and let you "
            "choose analysis options before generating anything.</p>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        file_layout.addWidget(self.file_path_label, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        
        # Upload button
        upload_btn = QPushButton("Upload && Continue")
        upload_btn.setStyleSheet("background-color: #0d6efd; color: white; padding: 10px; font-weight: bold;")
        upload_btn.clicked.connect(self._upload_file)
        layout.addWidget(upload_btn)
        
        # Info box
        info_box = QLabel(
            "<h4>What this tool does</h4>"
            "<ul>"
            "<li>Reads variable and value labels from your Stata file</li>"
            "<li>Lets you generate weighted or unweighted frequency tables</li>"
            "<li>Optionally skips ID variables or continuous numeric variables</li>"
            "<li>Exports a formatted Excel workbook — one sheet per variable, plus a summary sheet</li>"
            "</ul>"
        )
        info_box.setWordWrap(True)
        info_box.setStyleSheet("background-color: #f8f9fa; padding: 15px; border-radius: 5px;")
        layout.addWidget(info_box)
        
        layout.addStretch()
        return page
    
    def _create_options_page(self):
        """Create the options/step 2 page."""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        
        # Create scroll area for the options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Dataset info
        info_label = QLabel("<h3>Step 2 — Dataset loaded</h3>")
        layout.addWidget(info_label)
        
        self.dataset_info_label = QLabel("")
        layout.addWidget(self.dataset_info_label)
        
        # Variable table (collapsed by default)
        var_group = QGroupBox("Variable List (click to expand)")
        var_group.setCheckable(True)
        var_group.setChecked(False)
        var_layout = QVBoxLayout(var_group)
        
        self.var_table = QTableWidget()
        self.var_table.setColumnCount(5)
        self.var_table.setHorizontalHeaderLabels(["#", "Variable", "Type", "Label", "# Distinct"])
        self.var_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.var_table.setMaximumHeight(300)
        var_layout.addWidget(self.var_table)
        layout.addWidget(var_group)
        
        # Options header
        options_label = QLabel("<h3>Step 3 — Choose your analysis options</h3>")
        layout.addWidget(options_label)
        
        # Weighting options
        weight_group = QGroupBox("Weighting")
        weight_layout = QVBoxLayout(weight_group)
        
        self.weight_button_group = QButtonGroup()
        
        self.weight_none = QRadioButton("No weighting (unweighted frequencies)")
        self.weight_none.setChecked(True)
        self.weight_button_group.addButton(self.weight_none, 0)
        weight_layout.addWidget(self.weight_none)
        
        self.weight_variable = QRadioButton("Use a weight variable already in the dataset")
        self.weight_button_group.addButton(self.weight_variable, 1)
        weight_layout.addWidget(self.weight_variable)
        
        self.weight_var_combo = QComboBox()
        self.weight_var_combo.setEnabled(False)
        weight_layout.addWidget(self.weight_var_combo)
        
        self.weight_value_radio = QRadioButton("Apply a single weight value to every observation")
        self.weight_button_group.addButton(self.weight_value_radio, 2)
        weight_layout.addWidget(self.weight_value_radio)
        
        self.weight_value_input = QLineEdit()
        self.weight_value_input.setPlaceholderText("e.g. 100")
        self.weight_value_input.setEnabled(False)
        weight_layout.addWidget(self.weight_value_input)
        
        weight_help = QLabel(
            "<small>When using a weight value: this is applied to every observation, "
            "so frequencies reflect the population the sample represents (e.g., 1/probability of selection).</small>"
        )
        weight_help.setWordWrap(True)
        weight_layout.addWidget(weight_help)
        
        layout.addWidget(weight_group)
        
        # Connect weight radio buttons
        self.weight_none.toggled.connect(self._update_weight_fields)
        self.weight_variable.toggled.connect(self._update_weight_fields)
        self.weight_value_radio.toggled.connect(self._update_weight_fields)
        
        # Filter options
        filter_group = QGroupBox("Variable Filtering Options")
        filter_layout = QVBoxLayout(filter_group)
        
        self.exclude_id_vars = QCheckBox("Exclude ID variables (e.g. unique identifiers)")
        self.exclude_id_vars.setChecked(True)
        filter_layout.addWidget(self.exclude_id_vars)
        
        self.exclude_continuous = QCheckBox("Exclude continuous numeric variables (e.g. income, age in years)")
        filter_layout.addWidget(self.exclude_continuous)
        
        self.categorical_only = QCheckBox("Only tabulate categorical variables")
        filter_layout.addWidget(self.categorical_only)
        
        max_cat_layout = QHBoxLayout()
        max_cat_layout.addWidget(QLabel("Maximum categories before a variable is skipped:"))
        self.max_categories = QSpinBox()
        self.max_categories.setMinimum(2)
        self.max_categories.setMaximum(1000)
        self.max_categories.setValue(50)
        max_cat_layout.addWidget(self.max_categories)
        max_cat_layout.addStretch()
        filter_layout.addLayout(max_cat_layout)
        
        layout.addWidget(filter_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate Frequency Tables")
        generate_btn.setStyleSheet("background-color: #198754; color: white; padding: 10px; font-weight: bold;")
        generate_btn.clicked.connect(self._generate_tables)
        btn_layout.addWidget(generate_btn)
        
        start_over_btn = QPushButton("Start Over")
        start_over_btn.clicked.connect(self._start_over)
        btn_layout.addWidget(start_over_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        return page
    
    def _create_result_page(self):
        """Create the result/step 3 page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        result_label = QLabel("<h3>Frequency Tables Generated Successfully!</h3>")
        layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        open_file_btn = QPushButton("Open Excel File")
        open_file_btn.setStyleSheet("background-color: #0d6efd; color: white; padding: 10px; font-weight: bold;")
        open_file_btn.clicked.connect(self._open_output_file)
        btn_layout.addWidget(open_file_btn)
        
        save_as_btn = QPushButton("Save As...")
        save_as_btn.clicked.connect(self._save_as)
        btn_layout.addWidget(save_as_btn)
        
        start_over_btn = QPushButton("Start Over")
        start_over_btn.clicked.connect(self._start_over)
        btn_layout.addWidget(start_over_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return page
    
    def _browse_file(self):
        """Open file dialog to select .dta file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Stata Dataset",
            "",
            "Stata Files (*.dta);;All Files (*)"
        )
        if file_path:
            self.dta_path = Path(file_path)
            self.file_path_label.setText(str(self.dta_path))
    
    def _upload_file(self):
        """Load the selected file and show options page."""
        if not self.dta_path or not self.dta_path.exists():
            QMessageBox.warning(self, "No File", "Please select a .dta file first.")
            return
        
        try:
            # Load dataset
            self.df, self.meta = core.load_stata_dataset(self.dta_path)
            self.variable_overview = core.build_variable_overview(self.df, self.meta)
            
            # Update dataset info
            info_text = (
                f"<b>File:</b> {self.dta_path.name}<br>"
                f"<b>Observations:</b> {len(self.df):,}<br>"
                f"<b>Variables:</b> {self.df.shape[1]}"
            )
            self.dataset_info_label.setText(info_text)
            
            # Populate variable table
            self.var_table.setRowCount(len(self.variable_overview))
            for i, var_info in enumerate(self.variable_overview):
                self.var_table.setItem(i, 0, QTableWidgetItem(str(var_info["index"])))
                self.var_table.setItem(i, 1, QTableWidgetItem(var_info["name"]))
                self.var_table.setItem(i, 2, QTableWidgetItem(var_info["dtype"]))
                self.var_table.setItem(i, 3, QTableWidgetItem(var_info["label"]))
                self.var_table.setItem(i, 4, QTableWidgetItem(str(var_info["n_unique"])))
            
            # Populate weight variable combo
            self.weight_var_combo.clear()
            self.weight_var_combo.addItem("— choose a variable —")
            for col in self.df.columns:
                self.weight_var_combo.addItem(col)
            
            # Show options page
            self._show_page("options")
            
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error Loading File",
                f"Could not read the Stata file:\n\n{exc}"
            )
    
    def _update_weight_fields(self):
        """Enable/disable weight fields based on radio selection."""
        self.weight_var_combo.setEnabled(self.weight_variable.isChecked())
        self.weight_value_input.setEnabled(self.weight_value_radio.isChecked())
    
    def _generate_tables(self):
        """Generate frequency tables in background thread."""
        # Validate inputs
        weight_var = None
        weight_value = None
        
        if self.weight_variable.isChecked():
            if self.weight_var_combo.currentIndex() == 0:
                QMessageBox.warning(self, "Invalid Input", "Please select a weight variable.")
                return
            weight_var = self.weight_var_combo.currentText()
        
        elif self.weight_value_radio.isChecked():
            try:
                weight_value = float(self.weight_value_input.text())
                if weight_value <= 0:
                    raise ValueError("Weight must be positive")
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter a valid positive number for the weight value."
                )
                return
        
        # Prepare options
        options = {
            "exclude_id_vars": self.exclude_id_vars.isChecked(),
            "exclude_continuous": self.exclude_continuous.isChecked(),
            "categorical_only": self.categorical_only.isChecked(),
            "max_categories": self.max_categories.value(),
        }
        
        # Select output path
        default_name = f"Frequency_Tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Frequency Tables As",
            default_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not output_path:
            return
        
        self.output_path = Path(output_path)
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            "Processing variables...",
            "Cancel",
            0,
            len(self.df.columns),
            self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        
        # Create and start processing thread
        self.processing_thread = ProcessingThread(
            self.dta_path,
            self.output_path,
            self.dta_path.name,
            weight_var,
            weight_value,
            options
        )
        self.processing_thread.progress.connect(self._on_progress)
        self.processing_thread.finished.connect(self._on_finished)
        self.processing_thread.error.connect(self._on_error)
        
        self.progress_dialog.canceled.connect(self.processing_thread.terminate)
        self.processing_thread.start()
    
    def _on_progress(self, current, total, varname):
        """Update progress dialog."""
        self.progress_dialog.setMaximum(total)
        self.progress_dialog.setValue(current)
        self.progress_dialog.setLabelText(f"Processing variable {current}/{total}: {varname}")
    
    def _on_finished(self, result):
        """Handle successful completion."""
        self.progress_dialog.close()
        
        # Format result text
        summary = result["summary"]
        result_html = "<h4>Summary</h4><table border='1' cellpadding='5'>"
        for key, value in summary.items():
            result_html += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
        result_html += "</table>"
        
        if result["skipped"]:
            result_html += "<h4>Skipped Variables</h4><table border='1' cellpadding='5'>"
            result_html += "<tr><th>Variable</th><th>Reason</th></tr>"
            for item in result["skipped"]:
                result_html += f"<tr><td>{item['Variable']}</td><td>{item['Reason']}</td></tr>"
            result_html += "</table>"
        else:
            result_html += "<p><i>All variables were processed successfully.</i></p>"
        
        result_html += f"<p><b>Output saved to:</b><br>{self.output_path}</p>"
        
        self.result_text.setHtml(result_html)
        self._show_page("result")
    
    def _on_error(self, error_msg):
        """Handle processing error."""
        self.progress_dialog.close()
        QMessageBox.critical(
            self,
            "Processing Error",
            f"An error occurred while generating the frequency tables:\n\n{error_msg}"
        )
    
    def _open_output_file(self):
        """Open the generated Excel file with the default application."""
        if self.output_path and self.output_path.exists():
            import platform
            import subprocess
            
            if platform.system() == 'Windows':
                import os
                os.startfile(self.output_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.output_path])
            else:  # Linux
                subprocess.run(['xdg-open', self.output_path])
        else:
            QMessageBox.warning(self, "File Not Found", "The output file could not be found.")
    
    def _save_as(self):
        """Save the output file to a different location."""
        if not self.output_path or not self.output_path.exists():
            QMessageBox.warning(self, "No File", "No output file available.")
            return
        
        new_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            str(self.output_path),
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if new_path:
            try:
                shutil.copy2(self.output_path, new_path)
                QMessageBox.information(self, "Success", f"File saved to:\n{new_path}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{exc}")
    
    def _start_over(self):
        """Reset the application to the upload page."""
        self.dta_path = None
        self.df = None
        self.meta = None
        self.output_path = None
        self.variable_overview = []
        self.file_path_label.setText("No file selected")
        self._show_page("upload")


def main():
    """Entry point for the desktop application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Frequency Table Generator")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
