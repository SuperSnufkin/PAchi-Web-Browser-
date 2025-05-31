import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QAction,
    QTabWidget, QWidget, QVBoxLayout, QMessageBox, QStyleFactory
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEngineProfile, QWebEngineSettings, QWebEnginePage
)
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPalette

AD_DOMAINS = [
    "doubleclick.net", "googlesyndication.com", "ads.yahoo.com",
    "adnxs.com", "adform.net", "adsafeprotected.com", "pubmatic.com",
    "moatads.com", "scorecardresearch.com", "zedo.com", "taboola.com",
    "googletagmanager.com", "google-analytics.com", "facebook.net",
    "facebook.com", "twitter.com", "quantserve.com"
]

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        host = info.requestUrl().host()
        if any(domain in host for domain in AD_DOMAINS):
            info.block(True)

class PrivateProfile(QWebEngineProfile):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRequestInterceptor(AdBlockInterceptor())
        self.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.setPersistentStoragePath("")

        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        settings.setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)

class BrowserTab(QWidget):
    def __init__(self, url="https://duckduckgo.com"):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.profile = PrivateProfile()
        self.web = QWebEngineView()
        self.page = QWebEnginePage(self.profile, self.web)
        self.web.setPage(self.page)
        # Aseguramos que url sea string antes de pasarlo a QUrl
        if not isinstance(url, str):
            url = "https://duckduckgo.com"
        self.web.load(QUrl(url))
        self.layout.addWidget(self.web)
        self.setLayout(self.layout)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pachi Web Browser - Modo Oscuro")
        self.setGeometry(200, 200, 1000, 700)

        app.setStyle(QStyleFactory.create("Fusion"))
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, Qt.black)
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, Qt.black)
        dark_palette.setColor(QPalette.AlternateBase, Qt.gray)
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, Qt.black)
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Highlight, Qt.darkGray)
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(dark_palette)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.cerrar_pestania)
        self.setCentralWidget(self.tabs)

        nav_bar = QToolBar("Navegación")
        self.addToolBar(nav_bar)

        nueva_pestania_btn = QAction("🗂 Nueva pestaña", self)
        nueva_pestania_btn.triggered.connect(self.nueva_pestania)
        nav_bar.addAction(nueva_pestania_btn)

        nueva_privada_btn = QAction("🕵 Nueva ventana privada", self)
        nueva_privada_btn.triggered.connect(self.nueva_ventana_privada)
        nav_bar.addAction(nueva_privada_btn)

        acerca_btn = QAction("ℹ Acerca de", self)
        acerca_btn.triggered.connect(self.mostrar_acerca_de)
        nav_bar.addAction(acerca_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.ir_a_url)
        nav_bar.addWidget(self.url_bar)

        recargar_btn = QAction("⟳", self)
        recargar_btn.triggered.connect(lambda: self.tab_actual().web.reload())
        nav_bar.addAction(recargar_btn)

        self.nueva_pestania()

    def tab_actual(self):
        return self.tabs.currentWidget()

    # Corregido: capturamos checked y no lo usamos
    def nueva_pestania(self, url="https://duckduckgo.com", checked=False):
        # url puede ser bool si llamado desde QAction, entonces corregimos:
        if isinstance(url, bool):
            url = "https://duckduckgo.com"
        nueva = BrowserTab(url)
        index = self.tabs.addTab(nueva, "Nueva pestaña")
        self.tabs.setCurrentIndex(index)
        nueva.web.urlChanged.connect(self.actualizar_url)
        nueva.web.loadFinished.connect(lambda: self.tabs.setTabText(index, nueva.web.page().title()))

    def nueva_ventana_privada(self):
        nueva_ventana = Browser()
        nueva_ventana.show()

    def ir_a_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.tab_actual().web.load(QUrl(url))

    def actualizar_url(self, url):
        self.url_bar.setText(url.toString())

    def cerrar_pestania(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            self.close()

    def mostrar_acerca_de(self):
        QMessageBox.information(
            self,
            "Acerca de",
            "🦊 Pachi Web Browser (Modo Oscuro)\n\n"
            "Hecho con ❤️ en Python y PyQt5\n"
            "Bloqueo de anuncios y rastreadores\n"
            "No guarda historial ni cookies\n\n"
            "Autor: Israel G. Bistrain y Pachi\n"
            "Síguenos en Mastodon: @supersnufkin@mastodon.social"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    navegador = Browser()
    navegador.show()
    sys.exit(app.exec_())
