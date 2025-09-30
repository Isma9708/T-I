#!/usr/bin/env python3
"""
Dispute Analysis Tool - Main Application Entry Point

This is the entry point for the Dispute Analysis Tool application.
It initializes the GUI with improved error handling.

Usage:
    python main.py
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.app import ModernMaterialAnalyzerApp

# Application metadata
__version__ = "1.0.0"
__app_name__ = "Dispute Analysis Tool"

def show_error_dialog(error_msg):
    """Display error in a message box"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Error al iniciar la aplicación")
    msg.setInformativeText(error_msg)
    msg.setWindowTitle("Error de Inicialización")
    msg.setDetailedText(traceback.format_exc())
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def main():
    """Main application entry point with error handling"""
    try:
        # Initialize Qt application
        app = QApplication(sys.argv)
        app.setApplicationName(__app_name__)
        app.setApplicationVersion(__version__)
        app.setStyle('Fusion')  # Use Fusion style for better cross-platform consistency
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Create and show the main window
        print("Iniciando la ventana principal...")
        window = ModernMaterialAnalyzerApp()
        print("Mostrando la ventana...")
        window.show()
        print("Ejecutando la aplicación...")
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        error_msg = f"Se produjo un error: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        
        # Write to log file
        with open('logs/error.log', 'a') as f:
            f.write(f"{error_msg}\n")
            f.write(traceback.format_exc())
            f.write("\n---\n")
        
        # Show error dialog if QApplication exists
        if 'app' in locals():
            show_error_dialog(error_msg)
        
        return 1

if __name__ == "__main__":
    main()