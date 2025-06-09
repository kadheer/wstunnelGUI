import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QLineEdit, QFormLayout,
    QMenuBar, QFileDialog, QMessageBox, QTabWidget
)
from PyQt6.QtGui import QAction


class WstunnelGUIApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wstunnel GUI")
        self.setFixedSize(800, 600)
        
       
        self.current_file = None
        self.connection_active = False

        self.create_menu_bar()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create tab widget for configuration
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create server and client tabs
        self.create_server_tab()
        self.create_client_tab()

        # Status and activation panel at the bottom
        status_panel = QGroupBox("Connection Status")
        status_layout = QHBoxLayout(status_panel)

        # Connection status
        self.status_label = QLabel("Not connected!")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        
        # Activate button
        self.activate_button = QPushButton("Activate")
        self.activate_button.setStyleSheet("font-size: 14px;")
        self.activate_button.clicked.connect(self.toggle_connection)

        status_layout.addWidget(self.status_label, 1)
        status_layout.addWidget(self.activate_button)

        main_layout.addWidget(status_panel)

    def create_server_tab(self):
        """Create the server configuration tab"""
        server_tab = QWidget()
        server_layout = QFormLayout(server_tab)

        #Add the fields to the server parameters here (Use addRow to make it easier):
        self.server_port_number = QLineEdit()
        server_layout.addRow(QLabel("Listen on port number:"), self.server_port_number)
        

        self.tab_widget.addTab(server_tab, "Server")

    def create_client_tab(self):
        """Create the client configuration tab"""
        client_tab = QWidget()
        client_layout = QFormLayout(client_tab)

        #Add the fields to the client parameters here (Use addRow to make it easier):
        self.client_port_number = QLineEdit()
        client_layout.addRow(QLabel("Destination port number:"), self.client_port_number)

        self.tab_widget.addTab(client_tab, "Client")

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open Config", self)
        open_action.triggered.connect(self.open_config)
        file_menu.addAction(open_action)

        save_action = QAction("Save Config", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Config As", self)
        save_as_action.triggered.connect(self.save_config_as)
        file_menu.addAction(save_as_action)

        edit_menu = menu_bar.addMenu("Edit")

    def open_config(self):
        if self.connection_active:
            QMessageBox.warning(self, "Connection Active", "Cannot load config while connection is active")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Config File", "", "WireGuard Config Files (*.conf);;All Files (*)"
        )
        
        if file_path:
            try:
                self.current_file = file_path
                QMessageBox.information(
                    self, "Config Loaded", 
                    f"Config file loaded from:\n{file_path}\n\n(Actual loading not implemented in this example)"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load config:\n{str(e)}")

    def save_config(self):
        if not self.current_file:
            self.save_config_as()
            return
        
        try:
            QMessageBox.information(
                self, "Config Saved", 
                f"Config saved to:\n{self.current_file}\n\n(Actual saving not implemented in this example)"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config:\n{str(e)}")

    def save_config_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Config File", "", "WireGuard Config Files (*.conf);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.conf'):
                file_path += '.conf'
            self.current_file = file_path
            self.save_config()

    def toggle_connection(self):
        if self.connection_active:
            self.deactivate_connection()
        else:
            self.activate_connection()

    def activate_connection(self):
        # Freeze the configuration tabs
        self.tab_widget.setEnabled(False)
        self.connection_active = True
        
        # Update status
        self.status_label.setText("Connected!")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        self.activate_button.setText("Deactivate")

        # Determine which tab is active
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Server tab
            config_type = "Server"
            QMessageBox.information(self, "Connection Started", "Server configuration activated")
        else:  # Client tab
            config_type = "Client"
            QMessageBox.information(self, "Connection Started", "Client configuration activated")

    def deactivate_connection(self):
        # Unfreeze the configuration tabs
        self.tab_widget.setEnabled(True)
        self.connection_active = False
        
        # Update status
        self.status_label.setText("Not connected!")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        self.activate_button.setText("Activate")

        QMessageBox.information(self, "Connection Stopped", "Connection deactivated")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WstunnelGUIApp()
    window.show()
    sys.exit(app.exec())