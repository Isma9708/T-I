"""
Dispute Analysis Tool - Modern Professional PyQt5 Application
"""

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QFrame, QSizePolicy,
    QHeaderView, QTabWidget, QTextBrowser, QDialog, QRadioButton, QButtonGroup, QCheckBox
)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Importing from the correct folder structure
from data.loader import load_dataframes
from processing.states import add_custom_abbreviation
from processing.enrich import enrich_billback_table, enrich_ppm_table
from processing.analyze import analyze_materials
# Importing the new visualization and reports modules
from processing.visualize import create_variance_summary, create_detail_plots, save_visualizations
from processing.reports import generate_summary_report, export_results
# Importing from gui.styles instead of styles.qt_styles
from gui.styles import Colors, Typography, Layout, get_modern_style

class MatplotlibCanvas(FigureCanvas):
    """Canvas for displaying matplotlib charts in PyQt5"""
    def __init__(self, figure=None, parent=None):
        if figure is None:
            figure = plt.figure(figsize=(8, 6))
        super().__init__(figure)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

class VisualizationDialog(QDialog):
    """Dialog for displaying data visualizations"""
    def __init__(self, figure, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Canvas and toolbar for matplotlib figure
        canvas = MatplotlibCanvas(figure, self)
        toolbar = NavigationToolbar(canvas, self)
        
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        
        # Button to close the dialog
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_close.setObjectName("primaryButton")
        btn_close.setMaximumWidth(Layout.BUTTON_WIDTH_MEDIUM)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        self.setStyleSheet(get_modern_style())

class ReportFormatDialog(QDialog):
    """Dialog for selecting the report format"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Format")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(Layout.PADDING_MEDIUM)
        
        # Title
        title = QLabel("Select report format")
        title.setObjectName("filterLabel")
        layout.addWidget(title)
        
        # Radio button group for formats
        self.radio_group = QButtonGroup(self)
        
        self.html_radio = QRadioButton("HTML (Recommended)")
        self.markdown_radio = QRadioButton("Markdown")
        self.text_radio = QRadioButton("Plain text")
        
        self.html_radio.setChecked(True)
        
        self.radio_group.addButton(self.html_radio, 1)
        self.radio_group.addButton(self.markdown_radio, 2)
        self.radio_group.addButton(self.text_radio, 3)
        
        layout.addWidget(self.html_radio)
        layout.addWidget(self.markdown_radio)
        layout.addWidget(self.text_radio)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setObjectName("secondaryButton")
        
        self.btn_generate = QPushButton("Generate")
        self.btn_generate.clicked.connect(self.accept)
        self.btn_generate.setObjectName("primaryButton")
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_generate)
        
        layout.addLayout(btn_layout)
        self.setStyleSheet(get_modern_style())
    
    def get_selected_format(self):
        """Gets the selected format"""
        if self.html_radio.isChecked():
            return "html"
        elif self.markdown_radio.isChecked():
            return "markdown"
        else:
            return "text"

class ReportViewerDialog(QDialog):
    """Dialog for viewing reports"""
    def __init__(self, content, format_type, title="Analysis Report", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Report content
        self.text_browser = QTextBrowser()
        if format_type == "html":
            self.text_browser.setHtml(content)
        else:
            self.text_browser.setPlainText(content)
            
        layout.addWidget(self.text_browser)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_report)
        self.btn_save.setObjectName("accentButton")
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.setObjectName("primaryButton")
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        self.format_type = format_type
        self.content = content
        self.setStyleSheet(get_modern_style())
    
    def save_report(self):
        """Saves the report to a file"""
        extensions = {
            "html": "*.html",
            "markdown": "*.md",
            "text": "*.txt"
        }
        file_extension = extensions.get(self.format_type, "*.txt")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Report",
            os.path.expanduser("~/Documents"),
            f"Files ({file_extension})"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.content)
                QMessageBox.information(self, "Save Report", "Report saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving the report: {str(e)}")

class ModernMaterialAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dispute Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)
        self.result_df = pd.DataFrame()
        self.enriched_billback_df = None
        self.enriched_ppm_df = None
        self.states_df = None
        self.setStyleSheet(get_modern_style())
        self.init_ui()
        self.load_dropdowns()

    def init_ui(self):
        # Main container
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(Layout.PADDING_XL, Layout.PADDING_XL, Layout.PADDING_XL, Layout.PADDING_XL)
        main_layout.setSpacing(Layout.PADDING_LARGE)
        
        # Card container
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(Layout.PADDING_LARGE)
        card_layout.setContentsMargins(Layout.PADDING_XXL, Layout.PADDING_XXL, Layout.PADDING_XXL, Layout.PADDING_XXL)

        # Header section
        title = QLabel("Dispute Analysis Tool")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        subtitle = QLabel("Compare materials and rebates efficiently")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {Colors.GRAY_MEDIUM};")
        separator.setFixedHeight(1)
        card_layout.addWidget(separator)

        # Filters section
        filters_section = QLabel("Filter Options")
        filters_section.setObjectName("filterLabel")
        card_layout.addWidget(filters_section)
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(Layout.PADDING_LARGE)
        
        self.market_combo = QComboBox()
        self.brand_combo = QComboBox()
        self.year_combo = QComboBox()
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        
        filter_widgets = [
            {"label": "Market", "combo": self.market_combo, "icon": "🌎"},
            {"label": "Brand + Pk size", "combo": self.brand_combo, "icon": "🏷️"},
            {"label": "Year", "combo": self.year_combo, "icon": "📅"},
            {"label": "Month", "combo": self.month_combo, "icon": "📆"}
        ]
        
        for item in filter_widgets:
            vbox = QVBoxLayout()
            vbox.setSpacing(Layout.PADDING_SMALL)
            
            label_text = f"{item['icon']} {item['label']}"
            lbl = QLabel(label_text)
            lbl.setObjectName("filterLabel")
            
            combo = item['combo']
            combo.setMinimumWidth(Layout.BUTTON_WIDTH_LARGE)
            
            vbox.addWidget(lbl)
            vbox.addWidget(combo)
            filter_layout.addLayout(vbox)
        
        card_layout.addLayout(filter_layout)

        # Actions section
        actions_section = QLabel("Actions")
        actions_section.setObjectName("filterLabel")
        card_layout.addWidget(actions_section)
        
        # Add tabs for better organization of actions
        tabs = QTabWidget()
        
        # Analysis tab
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # Analysis buttons
        btn_analysis_layout = QHBoxLayout()
        btn_analysis_layout.setSpacing(Layout.PADDING_MEDIUM)
        
        self.btn_execute = QPushButton("Execute Analysis")
        self.btn_execute.setObjectName("primaryButton")
        self.btn_execute.setCursor(Qt.PointingHandCursor)
        self.btn_execute.clicked.connect(self.execute_analysis)
        btn_analysis_layout.addWidget(self.btn_execute)
        
        self.btn_clear = QPushButton("Clear Filters")
        self.btn_clear.setObjectName("secondaryButton")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_all)
        btn_analysis_layout.addWidget(self.btn_clear)
        
        self.btn_export = QPushButton("Export to Excel")
        self.btn_export.setObjectName("accentButton")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_to_excel)
        btn_analysis_layout.addWidget(self.btn_export)
        
        analysis_layout.addLayout(btn_analysis_layout)
        tabs.addTab(analysis_tab, "Analysis")
        
        # Visualization tab
        visualization_tab = QWidget()
        visualization_layout = QVBoxLayout(visualization_tab)
        
        # Visualization options
        viz_options_layout = QVBoxLayout()
        
        viz_header = QLabel("Select visualizations to generate:")
        viz_header.setObjectName("filterLabel")
        viz_options_layout.addWidget(viz_header)
        
        # Checkboxes for visualization types
        self.viz_summary_check = QCheckBox("Variance summary")
        self.viz_summary_check.setChecked(True)
        viz_options_layout.addWidget(self.viz_summary_check)
        
        self.viz_detail_check = QCheckBox("Detailed charts")
        self.viz_detail_check.setChecked(True)
        viz_options_layout.addWidget(self.viz_detail_check)
        
        # Visualization buttons
        btn_viz_layout = QHBoxLayout()
        
        self.btn_generate_viz = QPushButton("Generate Visualizations")
        self.btn_generate_viz.setObjectName("primaryButton")
        self.btn_generate_viz.clicked.connect(self.show_visualizations)
        btn_viz_layout.addWidget(self.btn_generate_viz)
        
        self.btn_save_viz = QPushButton("Save Visualizations")
        self.btn_save_viz.setObjectName("secondaryButton")
        self.btn_save_viz.clicked.connect(self.save_all_visualizations)
        btn_viz_layout.addWidget(self.btn_save_viz)
        
        visualization_layout.addLayout(viz_options_layout)
        visualization_layout.addLayout(btn_viz_layout)
        visualization_layout.addStretch()
        
        tabs.addTab(visualization_tab, "Visualization")
        
        # Reports tab
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        
        # Report options
        report_options = QLabel("Report options:")
        report_options.setObjectName("filterLabel")
        reports_layout.addWidget(report_options)
        
        # Report buttons
        btn_reports_layout = QHBoxLayout()
        
        self.btn_summary_report = QPushButton("Generate Summary Report")
        self.btn_summary_report.setObjectName("primaryButton")
        self.btn_summary_report.clicked.connect(self.show_summary_report)
        btn_reports_layout.addWidget(self.btn_summary_report)
        
        reports_layout.addLayout(btn_reports_layout)
        reports_layout.addStretch()
        
        tabs.addTab(reports_tab, "Reports")
        
        card_layout.addWidget(tabs)

        # Results section
        results_section = QLabel("Analysis Results")
        results_section.setObjectName("filterLabel")
        card_layout.addWidget(results_section)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Material", "At price", "Case in Part", "Part Amount", "Extended Part",
            "Net$", "Quantity", "Unit Rebate$", "Rebate", "VAR", "Comment"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setMinimumSectionSize(100)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(True)
        card_layout.addWidget(self.table)

        # Status and results
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)
        
        self.total_var_label = QLabel("")
        self.total_var_label.setObjectName("varLabel")
        self.total_var_label.setAlignment(Qt.AlignRight)
        status_layout.addWidget(self.total_var_label)
        
        card_layout.addLayout(status_layout)
        
        # Add card to main layout
        main_layout.addWidget(card)
        self.setCentralWidget(central_widget)

    def load_dropdowns(self):
        self.status_label.setText("Loading data...")
        QApplication.processEvents()
        
        # Real data loading
        try:
            _, item_ref_df, _, states = load_dataframes()
            self.states_df = add_custom_abbreviation(states)
            abbrs = sorted(self.states_df['Custom Abbreviation'].dropna().unique())
            item_ref_df["Brand + Pk size"] = item_ref_df[["Supp. Brand Desc.", "Package Size"]].fillna("").agg(' '.join, axis=1).str.strip()
            brands_pk_list = sorted(item_ref_df["Brand + Pk size"].dropna().unique())
        except Exception as e:
            self.status_label.setText(f"Error loading reference data: {str(e)}")
            abbrs = ["FL"]
            brands_pk_list = [""]
        
        # Years
        try:
            billback_df, _, ppm_df, _ = load_dataframes()
            billback_dates = pd.to_datetime(billback_df["Posting Period "], errors="coerce")
            bb_years = billback_dates.dt.year.dropna().unique()
            ppm_dates = pd.to_datetime(ppm_df["Start"], errors="coerce")
            ppm_years = ppm_dates.dt.year.dropna().unique()
            years = sorted(set(list(bb_years) + list(ppm_years)))
            years_list = [str(int(y)) for y in years if not pd.isnull(y)]
        except Exception as e:
            self.status_label.setText(f"Error loading date data: {str(e)}")
            years_list = []
        
        # Load combos
        self.market_combo.clear(); self.market_combo.addItems(abbrs)
        self.brand_combo.clear(); self.brand_combo.addItems(brands_pk_list)
        self.year_combo.clear(); self.year_combo.addItems(years_list)
        
        self.status_label.setText("Ready for analysis")

    def execute_analysis(self):
        self.status_label.setText("Running analysis...")
        QApplication.processEvents()
        
        selected_market = self.market_combo.currentText().strip()
        selected_brandpk = self.brand_combo.currentText().strip()
        try:
            selected_year = int(self.year_combo.currentText())
        except:
            selected_year = None
        selected_month = self.month_combo.currentText()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_number = months.index(selected_month) + 1 if selected_month in months else None

        if not selected_brandpk or not selected_year or not month_number:
            self.status_label.setText("Invalid selection")
            QMessageBox.warning(self, "Input Error", "Please select Market, Brand, Year and Month.")
            return

        try:
            tabla1, tabla2, tabla3, tabla4 = load_dataframes()
            tabla4 = add_custom_abbreviation(tabla4)
            self.enriched_billback_df = enrich_billback_table(tabla1, tabla4, tabla2)
            self.enriched_ppm_df = enrich_ppm_table(tabla3)
        except Exception as e:
            self.status_label.setText("File loading error")
            QMessageBox.critical(self, "File Error", f"Error loading Excel files: {e}")
            return

        billback = self.enriched_billback_df
        ppm = self.enriched_ppm_df

        billback_dates = pd.to_datetime(billback['Complete Date'], errors='coerce')
        ppm_dates = pd.to_datetime(ppm['Start'], errors='coerce')

        billback = billback[
            (billback['Custom Abbreviation'].astype(str).str.strip() == selected_market) &
            (billback['Brand + Pk size'].astype(str).str.strip() == selected_brandpk) &
            (billback_dates.dt.year == selected_year) &
            (billback_dates.dt.month == month_number)
        ].copy()

        ppm = ppm[
            (ppm['Dist Name.2'].astype(str).str.strip() == selected_market) &
            (ppm['ppm_Brand+pk size'].astype(str).str.strip() == selected_brandpk) &
            (ppm_dates.dt.year == selected_year) &
            (ppm_dates.dt.month == month_number)
        ].copy()

        if billback.empty or ppm.empty:
            self.status_label.setText("No matching records found")
            QMessageBox.information(self, "No Data", "No matching records for the selected filters.")
            return

        ppm.loc[:, 'Dist Item#'] = ppm['Dist Item#'].astype(str).str.strip()
        billback.loc[:, 'Material'] = billback['Material'].astype(str).str.strip()

        try:
            self.result_df = analyze_materials(billback, ppm, selected_brandpk)
        except Exception as e:
            self.status_label.setText("Analysis error")
            QMessageBox.critical(self, "Analysis Error", str(e))
            return

        # Populate table with results
        self.table.setRowCount(0)
        
        # List of numeric columns for formatting
        numeric_columns = ['At price', 'Case in Part', 'Part Amount', 'Extended Part', 
                          'Net$', 'Quantity', 'Unit Rebate$', 'Rebate', 'VAR']
        
        # Create mapping of column indices
        column_names = {}
        for col_idx in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col_idx)
            if header_item is not None:
                column_names[col_idx] = header_item.text()
        
        for row_idx, row in enumerate(self.result_df.itertuples(index=False)):
            self.table.insertRow(row_idx)
            
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem()
                
                # Verify index is in mapping before accessing
                col_name = column_names.get(col_idx, "")
                
                # Format numbers with commas and decimals
                if col_name in numeric_columns and pd.notna(value) and isinstance(value, (int, float)):
                    formatted_value = f"{value:,.2f}" if col_name not in ['Quantity', 'Case in Part'] else f"{value:,.0f}"
                    item.setText(formatted_value)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setText(str(value) if pd.notna(value) else "")
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Highlight VAR column with conditional formatting
                if col_name == 'VAR' and pd.notna(value) and isinstance(value, (int, float)):
                    if value > 0:
                        item.setForeground(QColor(Colors.SUCCESS))
                    elif value < 0:
                        item.setForeground(QColor(Colors.ERROR))
                
                self.table.setItem(row_idx, col_idx, item)
        
        # Auto-resize columns to content
        self.table.resizeColumnsToContents()

        # Show total VAR
        if not self.result_df.empty and 'VAR' in self.result_df.columns:
            total_var = self.result_df['VAR'].fillna(0).sum()
            self.total_var_label.setText(f"Total VAR difference: {total_var:,.2f}")
            
            # Add visual indicator based on VAR value
            if total_var > 0:
                self.total_var_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: {Typography.FONT_SIZE_LARGE}px; font-weight: bold;")
            elif total_var < 0:
                self.total_var_label.setStyleSheet(f"color: {Colors.ERROR}; font-size: {Typography.FONT_SIZE_LARGE}px; font-weight: bold;")
            else:
                self.total_var_label.setStyleSheet(f"color: {Colors.GOLD}; font-size: {Typography.FONT_SIZE_LARGE}px; font-weight: bold;")
        else:
            self.total_var_label.setText("Total VAR difference: 0.00")
            self.total_var_label.setStyleSheet(f"color: {Colors.GOLD}; font-size: {Typography.FONT_SIZE_LARGE}px; font-weight: bold;")

        self.status_label.setText("Analysis completed successfully")

    def clear_all(self):
        self.market_combo.setCurrentIndex(0)
        self.brand_combo.setCurrentIndex(0)
        self.year_combo.setCurrentIndex(0)
        self.month_combo.setCurrentIndex(0)
        self.table.clearContents()
        self.table.setRowCount(0)
        self.status_label.setText("Filters cleared")
        self.total_var_label.setText("")

    def export_to_excel(self):
        if not self.result_df.empty:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Excel Report",
                os.path.expanduser("~/Documents"),
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                    
                try:
                    self.status_label.setText("Exporting to Excel...")
                    QApplication.processEvents()
                    
                    self.result_df.to_excel(file_path, index=False)
                    
                    self.status_label.setText("Export completed successfully")
                    QMessageBox.information(self, "Export Success", f"Report exported successfully to:\n{file_path}")
                except Exception as e:
                    self.status_label.setText("Export failed")
                    QMessageBox.critical(self, "Export Error", f"Failed to export report: {str(e)}")
        else:
            QMessageBox.warning(self, "No Data", "There are no results to export. Please run an analysis first.")

    def show_visualizations(self):
        """Shows visualizations of analysis results"""
        if self.result_df.empty:
            QMessageBox.warning(self, "No Data", "No data to visualize. Please run an analysis first.")
            return
        
        self.status_label.setText("Generating visualizations...")
        QApplication.processEvents()
        
        try:
            # Generate visualizations according to selected options
            if self.viz_summary_check.isChecked():
                # Create variance summary visualization
                fig_summary = create_variance_summary(self.result_df)
                
                # Show in dialog
                dialog = VisualizationDialog(fig_summary, "Variance Summary", self)
                dialog.exec_()
            
            if self.viz_detail_check.isChecked():
                # Create detailed visualizations
                detail_figs = create_detail_plots(self.result_df)
                
                # Show each visualization in a separate dialog
                for title, fig in detail_figs.items():
                    dialog = VisualizationDialog(fig, f"Visualization: {title}", self)
                    dialog.exec_()
            
            self.status_label.setText("Visualizations generated successfully")
        except Exception as e:
            self.status_label.setText("Error generating visualizations")
            QMessageBox.critical(self, "Visualization Error", f"Error generating visualizations: {str(e)}")
    
    def save_all_visualizations(self):
        """Saves all visualizations to files"""
        if self.result_df.empty:
            QMessageBox.warning(self, "No Data", "No data to visualize. Please run an analysis first.")
            return
        
        # Request directory to save visualizations
        save_dir = QFileDialog.getExistingDirectory(
            self,
            "Select directory to save visualizations",
            os.path.expanduser("~/Documents")
        )
        
        if not save_dir:
            return
        
        self.status_label.setText("Saving visualizations...")
        QApplication.processEvents()
        
        try:
            # Generate visualizations
            figures = {}
            
            if self.viz_summary_check.isChecked():
                figures['variance_summary'] = create_variance_summary(self.result_df)
            
            if self.viz_detail_check.isChecked():
                detail_figs = create_detail_plots(self.result_df)
                figures.update(detail_figs)
            
            # Save visualizations
            saved_paths = save_visualizations(figures, save_dir)
            
            if saved_paths:
                self.status_label.setText(f"Visualizations saved to {save_dir}")
                QMessageBox.information(
                    self, 
                    "Visualizations Saved", 
                    f"{len(saved_paths)} visualizations have been saved to:\n{save_dir}"
                )
            else:
                self.status_label.setText("No visualizations were saved")
                QMessageBox.warning(self, "Notice", "No visualizations were saved")
        except Exception as e:
            self.status_label.setText("Error saving visualizations")
            QMessageBox.critical(self, "Error", f"Error saving visualizations: {str(e)}")
    
    def show_summary_report(self):
        """Shows a summary report of the results"""
        if self.result_df.empty:
            QMessageBox.warning(self, "No Data", "No data to generate the report. Please run an analysis first.")
            return
        
        # Request report format
        format_dialog = ReportFormatDialog(self)
        if format_dialog.exec_() != QDialog.Accepted:
            return
        
        report_format = format_dialog.get_selected_format()
        
        self.status_label.setText(f"Generating report in {report_format} format...")
        QApplication.processEvents()
        
        try:
            # Calculate statistics for the report
            stats = {
                'total_records': len(self.result_df),
                'perfect_matches': len(self.result_df[self.result_df['Comment'].isna()]),
                'mismatches': len(self.result_df[self.result_df['Comment'].str.contains('mismatch', na=False)]),
                'missing_deals': len(self.result_df[self.result_df['Comment'] == 'Missing Deal']),
                'ppm_only': len(self.result_df[self.result_df['Comment'] == 'PPM Only']),
                'total_variance': self.result_df['VAR'].fillna(0).sum(),
                'absolute_variance': self.result_df['VAR'].abs().fillna(0).sum(),
                'percent_matched': len(self.result_df[self.result_df['Comment'].isna()]) / len(self.result_df) * 100 if len(self.result_df) > 0 else 0
            }
            
            # Generate the report
            report_content = generate_summary_report(self.result_df, stats, report_format)
            
            # Show the report
            report_dialog = ReportViewerDialog(report_content, report_format, "Analysis Report", self)
            report_dialog.exec_()
            
            self.status_label.setText("Report generated successfully")
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Report Error", f"Error generating report: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform consistency
    window = ModernMaterialAnalyzerApp()
    window.show()
    sys.exit(app.exec_())
