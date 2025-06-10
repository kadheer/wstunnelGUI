import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QLineEdit, QFormLayout,
    QMenuBar, QFileDialog, QMessageBox, QTabWidget, QCheckBox
)
from PyQt6.QtGui import QAction
import json
import subprocess


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

        self.config_dic = {"server": {}, "client": {}}
        self.wstunnel_executable = None

    def create_server_tab(self):
        """Create the server configuration tab"""
        server_tab = QWidget()
        server_layout = QFormLayout(server_tab)

        # Add server parameters
        self.server_port_number = QLineEdit()
        server_layout.addRow(QLabel("Listen on port number:"), self.server_port_number)

        self.bind_address = QLineEdit("0.0.0.0")  # پیش‌فرض 0.0.0.0
        server_layout.addRow(QLabel("Bind Address:"), self.bind_address)

        self.tls_checkbox = QCheckBox("Enable TLS")
        server_layout.addRow(QLabel("TLS:"), self.tls_checkbox)

        self.tab_widget.addTab(server_tab, "Server")

    def create_client_tab(self):
        """Create the client configuration tab"""
        client_tab = QWidget()
        client_layout = QFormLayout(client_tab)

        # WebSocket URL
        self.ws_url_input = QLineEdit()
        client_layout.addRow(QLabel("WebSocket URL:"), self.ws_url_input)
        self.ws_url_input.editingFinished.connect(lambda: self.config_changed(self.ws_url_input))

        # Local Binding Address
        self.local_bind_input = QLineEdit("127.0.0.1:1080")
        client_layout.addRow(QLabel("Local Binding Address:"), self.local_bind_input)
        self.local_bind_input.editingFinished.connect(lambda: self.config_changed(self.local_bind_input))

        # Remote Target (optional)
        self.remote_target_input = QLineEdit()
        client_layout.addRow(QLabel("Remote Target (optional):"), self.remote_target_input)
        self.remote_target_input.editingFinished.connect(lambda: self.config_changed(self.remote_target_input))

        # TLS Ignore Cert Errors
        self.ignore_cert_checkbox = QCheckBox("Ignore TLS Certificate Errors")
        self.ignore_cert_checkbox.stateChanged.connect(lambda: self.config_changed(self.ignore_cert_checkbox))
        client_layout.addRow(self.ignore_cert_checkbox)

        # Proxy Settings
        self.proxy_input = QLineEdit()
        client_layout.addRow(QLabel("Proxy (e.g. socks5://127.0.0.1:9050):"), self.proxy_input)
        self.proxy_input.editingFinished.connect(lambda: self.config_changed(self.proxy_input))

        self.tab_widget.addTab(client_tab, "Client")

    def config_changed(self, widget):
        if widget == self.ws_url_input:
            self.config_dic["client"]["ws_url"] = widget.text()
        elif widget == self.local_bind_input:
            self.config_dic["client"]["local_bind"] = widget.text()
        elif widget == self.remote_target_input:
            self.config_dic["client"]["remote_target"] = widget.text()
        elif widget == self.ignore_cert_checkbox:
            self.config_dic["client"]["ignore_cert"] = widget.isChecked()
        elif widget == self.proxy_input:
            self.config_dic["client"]["proxy"] = widget.text()
        elif widget == self.client_port_number:
            self.config_dic["client"]["port"] = widget.text()
        elif widget == self.server_port_number:
            self.config_dic["server"]["port"] = widget.text()

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

        select_executable_action = QAction("Select Wstunnel Executable", self)
        select_executable_action.triggered.connect(self.select_wstunnel_executable)
        edit_menu.addAction(select_executable_action)

    def select_wstunnel_executable(self):
        """Open file dialog to select wstunnel executable"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Wstunnel Executable", "", )

        if file_path:
            self.wstunnel_executable = file_path

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
            with open(self.current_file, "w", encoding="utf-8") as f:
                json.dump(self.config_dic, f, indent=4)
            QMessageBox.information(
                self, "Config Saved",
                f"Config saved to:\n{self.current_file}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config:\n{str(e)}")

    def save_config_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Config File", "", "Wstunnel JSON Config Files (*.json);;All Files (*)"
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
            port = self.server_port_number.text()
            bind_addr = self.bind_address.text() or "0.0.0.0"
            cmd = f"wstunnel server --local-port {port} --bind-address {bind_addr}"
            if self.tls_checkbox.isChecked():
                cmd += " --tls"
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(result.stderr)
                QMessageBox.information(self, "Connection Started", "Server configuration activated")
            except Exception as e:
                self.deactivate_connection()
                QMessageBox.critical(self, "Error", f"Failed to start server: {str(e)}")
            else:  # Client tab
                config_type = "Client"
                ws_url = self.ws_url_input.text()
                local_bind = self.local_bind_input.text()
                remote_target = self.remote_target_input.text()
                ignore_cert = self.ignore_cert_checkbox.isChecked()
                proxy = self.proxy_input.text()

                if not ws_url or not local_bind:
                    QMessageBox.warning(self, "Missing Input", "WebSocket URL and Local Binding Address are required.")
                    self.deactivate_connection()
                    return

                # Split local bind
                try:
                    local_ip, local_port = local_bind.split(":")
                except ValueError:
                    QMessageBox.critical(self, "Input Error", "Local Binding Address must be in IP:PORT format.")
                    self.deactivate_connection()
                    return

                cmd = f"{self.wstunnel_executable or 'wstunnel'} client --remote-addr {ws_url} --local-addr {local_ip}:{local_port}"

                if remote_target:
                    cmd += f" --tunnel-addr {remote_target}"

                if ignore_cert:
                    cmd += " --insecure"

                if proxy:
                    cmd += f" --proxy {proxy}"

                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode != 0:
                        raise Exception(result.stderr)
                    QMessageBox.information(self, "Connection Started", "Client configuration activated")
                except Exception as e:
                    self.deactivate_connection()
                    QMessageBox.critical(self, "Error", f"Failed to start client: {str(e)}")

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