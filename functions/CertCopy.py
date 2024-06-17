import os
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from functions.CommandRunner import CommandRunner


# Класс CertCopy управляет копированием сертификатов на удаленные хосты
class CertCopy(QWidget):
    # Конструктор класса, инициализирует интерфейс
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.init_ui()

    # Метод для инициализации пользовательского интерфейса
    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Выберите файл сертификата:")
        layout.addWidget(self.label)

        self.cert_button = QPushButton("Выбрать файл")
        self.cert_button.clicked.connect(self.selectCertificate)
        layout.addWidget(self.cert_button)

        self.copy_button = QPushButton("Копировать сертификат")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copyCertificate)
        layout.addWidget(self.copy_button)

        self.cert_path = None

        # Scroll area for result label
        self.scroll_area = QScrollArea()
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setWordWrap(True)
        self.scroll_area.setWidget(self.result_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)
        layout.addWidget(self.scroll_area)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    # Метод для отображения результата выполнения команды
    def show_result(self, success, output, return_code):
        if success:
            result_text = f"Вывод команды:\n{output}\n\nКод завершения: {return_code}"
        else:
            result_text = "Произошла ошибка при выполнении"
        os.remove(self.destination_path)
        self.result_label.setText(result_text)
        self.result_label.setVisible(True)
        self.copy_button.setEnabled(True)

        self.scroll_area.setVisible(True)

    # Метод для выбора файла сертификата
    def selectCertificate(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.cert_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл сертификата", "",
                                                        "Certificate Files (*.crt *.pem);;All Files (*)",
                                                        options=options)

        if self.cert_path:
            self.copy_button.setEnabled(True)
            self.label.setText(f"Выбранный файл: {self.cert_path}")
        else:
            self.copy_button.setEnabled(False)
            self.label.setText("Файл не выбран")

    # Метод для копирования сертификата на удаленные хосты
    def copyCertificate(self):
        if self.cert_path:
            cert_filename = os.path.basename(self.cert_path)
            saltStack_path = '/srv/salt/'

            self.destination_path = os.path.join(saltStack_path, cert_filename)
            shutil.copy(self.cert_path, self.destination_path)
            hosts = ','.join(map(str, self.getSelectedItems(self.tree_widget.tree_widget.invisibleRootItem())))
            salt_command = f"salt -L '{hosts}' cp.get_file salt://{cert_filename} /etc/ssl/certs/"
            self.thread = CommandRunner(salt_command, self)
            self.thread.finished.connect(self.show_result)
            self.thread.start()

    # Метод для получения выбранных элементов из дерева
    def getSelectedItems(self, parent_item):
        selected_items = []
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            if child_item.childCount() == 0 and child_item.checkState(0) == Qt.Checked:
                selected_items.append(child_item.text(0))
            elif child_item.childCount() > 0:
                selected_items.extend(self.getSelectedItems(child_item))
        return selected_items

