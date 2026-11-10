import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon

class MistralWebPage(QWebEnginePage):
    def __init__(self, profile, parent):
        super().__init__(profile, parent)
        # I pulsanti "copia" dei siti usano navigator.clipboard,
        # che chiede il permesso: qui lo concediamo invece di negarlo in silenzio.
        self.permissionRequested.connect(self._on_permission)
        self.featurePermissionRequested.connect(self._on_feature_permission)

    def _on_permission(self, permission):
        try:
            from PySide6.QtWebEngineCore import QWebEnginePermission
            if permission.permissionType() in (
                QWebEnginePermission.PermissionType.ClipboardReadWrite,
                QWebEnginePermission.PermissionType.ClipboardSanitizedWrite,
            ):
                permission.grant()
            else:
                permission.deny()
        except Exception:
            permission.grant()

    def _on_feature_permission(self, url, feature):
        # Compatibilità con Qt più vecchi: concede ClipboardReadWrite
        self.setFeaturePermission(url, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    def createWindow(self, _type):
        return self
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mistral AI")
        self.resize(1200, 800)

        cache_path = os.path.expanduser("~/.cache/mistral-desktop")
        data_path = os.path.expanduser("~/.local/share/mistral-desktop")
        
        os.makedirs(cache_path, exist_ok=True)
        os.makedirs(data_path, exist_ok=True)

        self.profile = QWebEngineProfile("MistralProfile", None)
        self.profile.setPersistentStoragePath(data_path)
        self.profile.setCachePath(cache_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

        self.page = MistralWebPage(self.profile, self)
        self.view = QWebEngineView()
        self.view.setPage(self.page)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.view.load(QUrl("https://chat.mistral.ai"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("mistral-desktop")
    app.setDesktopFileName("mistral-desktop")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
