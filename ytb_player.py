import pickle
import random
from datetime import datetime
import subprocess
import sys
from threading import Thread
from math import sqrt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pytube
import pandas as pd


class YoutubePlayer(QMainWindow):
    def __init__(self):
        super(YoutubePlayer, self).__init__()

        self.url = "https://www.youtube.com/watch?v=HmZKgaHa3Fg"
        self.urlId = self.url.split('v=')[-1]

        self.defaultResolutions = {
            "hd1440": "2560 x 1440",
            "hd1080": "1920 x 1080",
            "720": "1280 x 720",
            "480": "854 x 480",
            "360": "640 x 360",
            "240": "426 x 240"
        }

        self.latencyList = []
        self.jitterList = []

        try:
            self.dataframe = pd.read_csv('network-stats.csv', index_col=False)
        except FileNotFoundError:
            self.dataframe = pd.DataFrame(columns=['date', 'latency', 'jitter', 'packetloss'])

        ###################################################################################

        self.setWindowTitle('Dashboard LA/P13 - Victor-Alexis PACAUD / Thibault RICHEL')
        self.setMinimumSize(1200, 600)

        self.centralWidget = QWidget()
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        # --------------------------------------------------------------------------------- QWebView

        randomResolution = False
        self.videoQuality, self.codec, self.framerate = self.getQualityCodecFramerate(randomResolution)
        if int(self.videoQuality) > 720:
            self.videoQuality = 'hd' + str(self.videoQuality)
        self.webView = QWebEngineView()

        htmlString = f"""
                    <iframe 
                            src="https://www.youtube.com/embed/{self.urlId}?autoplay=0&showinfo=0&
                            vq={self.videoQuality}&controls=0"
                            width="100%" height="100%" 
                            frameborder="0" allowautoplay>
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
        self.statsWidget.setMaximumWidth(round(self.width() * 25 / 100))
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

        self.latencyValue = QLabel("Click on 'Start measuring'")
        self.latencyValue.setStyleSheet(gridValue)

        self.jitterLabel = QLabel("Jitter :")
        self.jitterLabel.setStyleSheet(gridLabel)

        self.jitterValue = QLabel("Click on 'Start measuring'")
        self.jitterValue.setStyleSheet(gridValue)

        self.packetLossLabel = QLabel("Packet Loss :")
        self.packetLossLabel.setStyleSheet(gridLabel)

        self.packetLossValue = QLabel("Click on 'Start measuring'")
        self.packetLossValue.setStyleSheet(gridValue)

        self.networkContentLayout.addWidget(self.latencyLabel, 0, 0)
        self.networkContentLayout.addWidget(self.latencyValue, 0, 1)
        self.networkContentLayout.addWidget(self.jitterLabel, 1, 0)
        self.networkContentLayout.addWidget(self.jitterValue, 1, 1)
        self.networkContentLayout.addWidget(self.packetLossLabel, 2, 0)
        self.networkContentLayout.addWidget(self.packetLossValue, 2, 1)

        # Video stats
        self.videoStatsLabel = QLabel("Video informations :")
        self.videoStatsLabel.setMaximumHeight(40)
        self.videoStatsLabel.setStyleSheet(subtitle)

        self.videoContentWidget = QWidget()
        self.videoContentLayout = QGridLayout()
        self.videoContentWidget.setLayout(self.videoContentLayout)

        self.codecLabel = QLabel("Codec :")
        self.codecLabel.setStyleSheet(gridLabel)

        self.codecValue = QLabel("Click on 'Start measuring'")
        self.codecValue.setStyleSheet(gridValue)

        self.resolutionLabel = QLabel("Resolution :")
        self.resolutionLabel.setStyleSheet(gridLabel)

        self.resolutionValue = QLabel("Click on 'Start measuring'")
        self.resolutionValue.setStyleSheet(gridValue)

        self.framerateLabel = QLabel("Frame rate :")
        self.framerateLabel.setStyleSheet(gridLabel)

        self.framerateValue = QLabel("Click on 'Start measuring'")
        self.framerateValue.setStyleSheet(gridValue)

        self.videoContentLayout.addWidget(self.codecLabel, 0, 0)
        self.videoContentLayout.addWidget(self.codecValue, 0, 1)
        self.videoContentLayout.addWidget(self.resolutionLabel, 1, 0)
        self.videoContentLayout.addWidget(self.resolutionValue, 1, 1)
        self.videoContentLayout.addWidget(self.framerateLabel, 2, 0)
        self.videoContentLayout.addWidget(self.framerateValue, 2, 1)

        self.btnStartMeasuring = QPushButton("Start measuring")
        self.btnStartMeasuring.clicked.connect(self.startMeasuringLoop)

        self.btnStopGetScore = QPushButton("Stop and get QoS score")
        self.btnStopGetScore.clicked.connect(self.displayScoreQOS)
        self.btnStopGetScore.setEnabled(False)

        # Adding widgets
        self.statsLayout.addWidget(self.title)
        self.statsLayout.addWidget(self.networkStatsLabel)
        self.statsLayout.addWidget(self.networkContentWidget)
        self.statsLayout.addWidget(self.videoStatsLabel)
        self.statsLayout.addWidget(self.videoContentWidget)
        self.statsLayout.addWidget(self.btnStartMeasuring)
        self.statsLayout.addWidget(self.btnStopGetScore)

        ###################################################################################

        # Measuring loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.startThreads)

        ###################################################################################

        self.mainLayout.addWidget(self.webView)
        self.mainLayout.addWidget(self.statsWidget)
        self.showMaximized()

    def closeEvent(self, event):
        quitter = QMessageBox()
        quitter.setText("Attention !")
        quitter.setInformativeText("Save network stats in csv file?")
        quitter.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        quitter.setDefaultButton(QMessageBox.Ok)
        reply = quitter.exec_()
        if reply == QMessageBox.Ok:
            self.dataframe.to_csv('network-stats.csv', index=False)
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, event):
        self.statsWidget.setMaximumWidth(round(self.width() * 25 / 100))

    def startMeasuringLoop(self):
        self.btnStopGetScore.setEnabled(True)
        self.btnStartMeasuring.setEnabled(False)
        self.latencyValue.setText('collecting...')
        self.packetLossValue.setText('collecting...')
        self.jitterValue.setText('collecting...')
        self.timer.start(2000)

    def startThreads(self):
        self.resolutionValue.setText(self.defaultResolutions[str(self.videoQuality)])
        self.codecValue.setText(self.codec)
        self.framerateValue.setText(f'{str(self.framerate)} fps')

        thread1 = Thread(target=self.displayAllStats)
        thread1.start()

    def displayAllStats(self):
        latency, packetloss = self.getLatencyPacketloss()
        jitter = self.getJitter()
        self.latencyValue.setText(f"{latency} ms")
        self.jitterValue.setText(f"{jitter} ms")
        self.packetLossValue.setText(f"{packetloss} %")

        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.dataframe = self.dataframe.append({'date': now,
                                                'latency': str(latency) + 'ms',
                                                'jitter': str(jitter) + 'ms',
                                                'packetloss': str(packetloss) + '%'}, ignore_index=True)

    def getLatencyPacketloss(self):
        res = subprocess.check_output(f"serviceping {self.url} -c 1", shell=True).decode('utf-8')
        lines = res.split('\n')
        latency = packetloss = 'unknown'
        for li in lines:
            if 'time=' in li:
                latency = float(li.split('time=')[-1].split(' ')[0])
                self.latencyList.append(latency)
            if 'packet loss' in li:
                packetloss = float(li.split(', ')[2].split('%')[0])
        return latency, packetloss

    def getJitter(self):
        if len(self.latencyList) >= 5:
            measures = self.latencyList[-5:]
        else:
            measures = self.latencyList
        summ = jit = 0
        for lat in measures:
            summ += lat
        mean = summ / len(measures)
        jitters = [(mean - lat) ** 2 for lat in measures]
        for j in jitters:
            jit += j
        return round(sqrt(jit / len(jitters)), 2)

    def getQualityCodecFramerate(self, randomRes):
        vid = pytube.YouTube(self.url)
        streams = [stream for stream in vid.streams if not stream.is_progressive]
        results = []
        for i, s in enumerate(streams):
            if s.resolution is not None:
                resol = int(s.resolution.replace('p', ''))
                codec = vid.streams[i].video_codec.split('.')[0]
                rate = vid.streams[i].fps
                results.append((resol, codec, rate))
        if randomRes:
            final = random.choice(results)
        else:
            final = max(results, key=lambda x: x[0])
        return final

    def predictModel(self, height, width, frame_rate):
        self.timer.stop()

        filename = 'qos-model.pickle'
        loaded_model = pickle.load(open(filename, 'rb'))

        NewSample = {'resolution_height': [height],
                     'resolution_width': [width],
                     'frame_rate': [frame_rate],
                     }

        dfNew = pd.DataFrame(NewSample, columns=['resolution_height', 'resolution_width', 'frame_rate'])

        MOS_resultat = loaded_model.predict(dfNew)[0]

        return MOS_resultat

    def displayScoreQOS(self):
        height = self.defaultResolutions[str(self.videoQuality)].split(' x ')[0]
        width = self.defaultResolutions[str(self.videoQuality)].split(' x ')[1]
        score = self.predictModel(height, width, self.framerate)
        disp = QDialog()
        layout = QVBoxLayout()

        scoreLabel = QLabel(f"QoS score : <b>{score}/5</b>")
        scoreLabel.setStyleSheet("QLabel { font-size: 20px }")
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonbox.accepted.connect(disp.accept)

        layout.addWidget(scoreLabel)
        layout.addWidget(buttonbox)
        disp.setLayout(layout)
        disp.exec_()


if __name__ == '__main__':
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = YoutubePlayer()
    window.show()
    app.exec_()
