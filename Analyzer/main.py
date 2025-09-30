"""
Dispute Analysis Tool - Main Entry Point

This module serves as the entry point for the Dispute Analysis Tool application,
configuring logging, launching the GUI, and coordinating between components.
"""

import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication

# Configure logging
def configure_logging():
    """Configure application-wide logging"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log filename with timestamp
    log_file = os.path.join(log_dir, f"dispute_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure logging format and level
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured. Application starting...")
    return logger

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'PyQt5']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Error: Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Main application entry point"""
    # Configure logging
    logger = configure_logging()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing dependencies. Exiting.")
        sys.exit(1)
    
    try:
        # Import GUI app module
        from gui.app import ModernMaterialAnalyzerApp
        
        # Start the application
        logger.info("Starting GUI application")
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for better cross-platform consistency
        window = ModernMaterialAnalyzerApp()
        window.show()
        
        # Execute application loop
        logger.info("GUI application initialized and shown")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(f"Error starting application: {str(e)}", exc_info=True)
        
        # Show error message if possible
        try:
            from PyQt5.QtWidgets import QMessageBox
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Application Error")
            error_box.setText("An error occurred while starting the application.")
            error_box.setDetailedText(str(e))
            error_box.exec_()
        except:
            print(f"Critical error: {str(e)}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
