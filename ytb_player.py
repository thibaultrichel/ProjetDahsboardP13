import subprocess
import sys
from threading import Thread
from math import sqrt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView


class YoutubePlayer(QMainWindow):
    def __init__(self):
        super(YoutubePlayer, self).__init__()

        self.url = "https://www.youtube.com/watch?v=HmZKgaHa3Fg"
        self.urlId = self.url.split('v=')[-1]

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

        htmlString = f"""
                    <iframe width="100%" height="100%" 
                            src="https://www.youtube.com/embed/{self.urlId}?rel=0&showinfo=0&autoplay=1"
                            frameborder="0">
                    </iframe>
                     """
        self.webView.setHtml(htmlString, QUrl(self.url))

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

        self.packetLossValue = QLabel("collecting...")
        self.packetLossValue.setStyleSheet(gridValue)

        self.bandwidthLabel = QLabel("Bandwidth (up/down) :")
        self.bandwidthLabel.setStyleSheet(gridLabel)

        self.bandwidthValue = QLabel("collecting...")
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

        self.startThreads()

    def resizeEvent(self, event):
        self.statsWidget.setMaximumWidth(round(self.width() * 35 / 100))

    def startThreads(self):
        thread1 = Thread(target=self.displayAllStats)
        thread1.start()

    def displayAllStats(self):
        latency, jitter, packetloss, upVal, upUnit, downVal, downUnit = self.getAllStats()
        self.latencyValue.setText(f"{latency} ms")
        self.jitterValue.setText(f"{jitter} ms")
        self.packetLossValue.setText(f"{packetloss} %")
        self.bandwidthValue.setText(f"{upVal} {upUnit}  /  {downVal} {downUnit}")

    def getAllStats(self):
        lats = []
        res = subprocess.check_output(f"serviceping {self.url} -c 5", shell=True).decode('utf-8')
        lines = res.split('\n')
        packetloss = 'unknown'

        for li in lines:
            if 'time=' in li:
                lat = float(li.split('time=')[-1].split(' ')[0])
                lats.append(lat)
            if 'packet loss' in li:
                packetloss = float(li.split(', ')[2].split('%')[0])

        summ = jit = 0
        for la in lats:
            summ += la
        mean = summ/len(lats)
        jitters = [(mean - lat)**2 for lat in lats]
        for j in jitters:
            jit += j
        jitter = round(sqrt(jit/len(jitters)), 2)
        latency = round(mean, 2)

        bw = subprocess.check_output("speedtest", shell=True).decode('utf-8')
        lines = bw.split('\n')
        upVal = downVal = downUnit = upUnit = 'unknown'
        for li in lines:
            if 'Download' in li:
                downVal = float(li.split(' ')[1])
                downUnit = li.split(' ')[-1]
            if 'Upload' in li:
                upVal = float(li.split(' ')[1])
                upUnit = li.split(' ')[-1]

        return latency, jitter, packetloss, upVal, upUnit, downVal, downUnit


if __name__ == '__main__':
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = YoutubePlayer()
    window.show()
    app.exec_()
