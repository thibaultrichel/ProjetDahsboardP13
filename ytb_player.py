import sys
import time
import threading
from math import sqrt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests


class YoutubePlayer(QMainWindow):
    def __init__(self):
        super(YoutubePlayer, self).__init__()

        ###################################################################################

        self.setWindowTitle('Dashboard LA/P13 - Victor-Alexis PACAUD / Thibault RICHEL')
        self.setMinimumSize(1200, 600)

        self.centralWidget = QWidget()
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        # --------------------------------------------------------------------------------- QWebView

        self.webView = QWebEngineView()

        htmlString = """
                    <iframe width="100%" height="100%" 
                            src="https://www.youtube.com/embed/HmZKgaHa3Fg?rel=0&showinfo=0&autoplay=1"
                            frameborder="0">
                    </iframe>
                     """
        self.webView.setHtml(htmlString, QUrl("https://www.youtube.com/watch?v=HmZKgaHa3Fg"))

        # --------------------------------------------------------------------------------- Stats

        # Stylesheets
        title = "QLabel { font: 30px; text-decoration: underline; font-weight: bold }"
        subtitle = "QLabel { font: 18px; text-decoration: underline }"
        gridLabel = "QLabel { font: 14px }"
        gridValue = "QLabel { font: 14px; font-weight: bold }"

        # Main widgets and layouts
        self.statsWidget = QWidget()
        self.statsWidget.setMinimumWidth(200)
        self.statsWidget.setMaximumWidth(round(self.width() * 35 / 100))
        self.statsLayout = QVBoxLayout()
        self.statsWidget.setLayout(self.statsLayout)

        self.title = QLabel("Statistics")
        self.title.setMaximumHeight(50)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(title)

        # Network stats
        self.networkStatsLabel = QLabel("Network informations :")
        self.networkStatsLabel.setMaximumHeight(40)
        self.networkStatsLabel.setStyleSheet(subtitle)

        self.networkContentWidget = QWidget()
        self.networkContentLayout = QGridLayout()
        self.networkContentWidget.setLayout(self.networkContentLayout)

        self.latencyLabel = QLabel("Latency :")
        self.latencyLabel.setStyleSheet(gridLabel)

        self.latencyValue = QLabel("collecting...")
        self.latencyValue.setStyleSheet(gridValue)

        self.jitterLabel = QLabel("Jitter :")
        self.jitterLabel.setStyleSheet(gridLabel)

        self.jitterValue = QLabel("collecting...")
        self.jitterValue.setStyleSheet(gridValue)

        self.packetLossLabel = QLabel("Packet Loss :")
        self.packetLossLabel.setStyleSheet(gridLabel)

        self.packetLossValue = QLabel("17 %")
        self.packetLossValue.setStyleSheet(gridValue)

        self.bandwidthLabel = QLabel("Bandwidth (up/down) :")
        self.bandwidthLabel.setStyleSheet(gridLabel)

        self.bandwidthValue = QLabel("27.43 Mbps / 27.43 Mbps")
        self.bandwidthValue.setStyleSheet(gridValue)

        self.networkContentLayout.addWidget(self.latencyLabel, 0, 0)
        self.networkContentLayout.addWidget(self.latencyValue, 0, 1)
        self.networkContentLayout.addWidget(self.jitterLabel, 1, 0)
        self.networkContentLayout.addWidget(self.jitterValue, 1, 1)
        self.networkContentLayout.addWidget(self.packetLossLabel, 2, 0)
        self.networkContentLayout.addWidget(self.packetLossValue, 2, 1)
        self.networkContentLayout.addWidget(self.bandwidthLabel, 3, 0)
        self.networkContentLayout.addWidget(self.bandwidthValue, 3, 1)

        # Video stats
        self.videoStatsLabel = QLabel("Video informations :")
        self.videoStatsLabel.setMaximumHeight(40)
        self.videoStatsLabel.setStyleSheet(subtitle)

        self.videoContentWidget = QWidget()
        self.videoContentLayout = QGridLayout()
        self.videoContentWidget.setLayout(self.videoContentLayout)

        self.codecLabel = QLabel("Codec :")
        self.codecLabel.setStyleSheet(gridLabel)

        self.codecValue = QLabel("h264")
        self.codecValue.setStyleSheet(gridValue)

        self.resolutionLabel = QLabel("Resolution :")
        self.resolutionLabel.setStyleSheet(gridLabel)

        self.resolutionValue = QLabel("1280×720")
        self.resolutionValue.setStyleSheet(gridValue)

        self.videoContentLayout.addWidget(self.codecLabel, 0, 0)
        self.videoContentLayout.addWidget(self.codecValue, 0, 1)
        self.videoContentLayout.addWidget(self.resolutionLabel, 1, 0)
        self.videoContentLayout.addWidget(self.resolutionValue, 1, 1)

        # Adding widgets
        self.statsLayout.addWidget(self.title)
        self.statsLayout.addWidget(self.networkStatsLabel)
        self.statsLayout.addWidget(self.networkContentWidget)
        self.statsLayout.addWidget(self.videoStatsLabel)
        self.statsLayout.addWidget(self.videoContentWidget)

        ###################################################################################

        self.mainLayout.addWidget(self.webView)
        self.mainLayout.addWidget(self.statsWidget)

        self.startThread()

    def resizeEvent(self, event):
        self.statsWidget.setMaximumWidth(round(self.width() * 35 / 100))

    def startThread(self):
        thread = threading.Thread(target=self.getAllStats)
        thread.start()

    def getAllStats(self):
        latency, jitter = self.getLatencyJitter()
        self.latencyValue.setText(f"{latency} ms")
        self.jitterValue.setText(f"{jitter} ms")

    @staticmethod
    def getLatencyJitter():
        lats = []
        for _ in range(5):
            lat = requests.get("https://www.youtube.com/watch?v=ihJZUux8ZOQ").elapsed.total_seconds() * 1000
            lats.append(lat)
            time.sleep(1)
        summ = jit = 0
        for la in lats:
            summ += la
        mean = summ/len(lats)
        jitters = [(mean - lat)**2 for lat in lats]
        for j in jitters:
            jit += j
        jitter = round(sqrt(jit/len(jitters)), 2)
        latency = round(mean, 2)
        return latency, jitter

    def getPacketLoss(self):
        pass

    def getVideoStats(self):
        pass


if __name__ == '__main__':
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = YoutubePlayer()
    window.show()
    app.exec_()
