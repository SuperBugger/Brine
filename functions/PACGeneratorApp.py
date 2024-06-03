from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class PACGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.proxyInput = QLineEdit(self)
        layout.addWidget(QLabel('Proxy (IP:Port)'))
        layout.addWidget(self.proxyInput)

        self.domainInput = QLineEdit(self)
        layout.addWidget(QLabel('Домены (example.ru,*.example.ru)'))
        layout.addWidget(self.domainInput)

        self.generateBtn = QPushButton('Сгенирировать и сохранить PAC File', self)
        self.generateBtn.clicked.connect(self.onGenerateAndSave)
        layout.addWidget(self.generateBtn)

        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
        self.setWindowTitle('PAC File')

    def onGenerateAndSave(self):
        proxy = self.proxyInput.text()
        domains = self.domainInput.text()
        pac_script = self.generate_pac(proxy, domains)

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить PAC File", "", "PAC Files (*.pac)", options=options)
        if fileName:
            with open(fileName, 'w') as file:
                file.write(pac_script)

    def generate_pac(self, proxy, domains):
        pac_script = "function FindProxyForURL(url, host) {\n"
        for domain in domains.split(','):
            pac_script += f"    if (shExpMatch(host, '{domain.strip()}')) return 'PROXY {proxy}';\n"
        pac_script += "    return 'DIRECT';\n"
        pac_script += "}"
        return pac_script
