import os
from tcp_latency import measure_latency
import requests
import time
import threading
import serviceping
import subprocess

# props = get_video_properties('/Users/thibaultrichel/Desktop/COURS/PARIS/Projet P13/vidtest.mp4')
#
# print(f'''
# Codec: {props['codec_name']}
# Resolution: {props['width']}×{props['height']}
# Aspect ratio: {props['display_aspect_ratio']}
# Frame rate: {props['avg_frame_rate']}
# ''')
import pytube

url = "https://www.youtube.com/watch?v=ihJZUux8ZOQ"


# os.system(f"ping youtube.com -c 5")

# lats = measure_latency('youtube.com', runs=5)
# print(lats)

# lats = []
#
# for i in range(5):
#     lat = requests.get(url).elapsed.total_seconds()*1000
#     lats.append(lat)
#     print(lat)
#     time.sleep(2)

#
# summ = jitter = 0
# for lat in lats:
#     summ += lat
#
# mean = summ/len(lats)
#
# jitters = [abs(mean - lat) for lat in lats]
# for jit in jitters:
#     jitter += jit
#
# jitter = jitter/len(lats)
#
# print(f"lats: {lats}")
# print(f"mean:{mean}")
# print(f"jitter:{jitter}")

# res = subprocess.check_output(f"serviceping {url} -c 5", shell=True).decode('utf-8')
# lines = res.split('\n')
# lats = []
# packetloss = 'unknown'
#
# for li in lines:
#     if 'time=' in li:
#         lat = float(li.split('time=')[-1].split(' ')[0])
#         lats.append(lat)
#     if 'packet loss' in li:
#         packetloss = float(li.split(', ')[2].split('%')[0])
#
#
# print(lats)
# print(f"{packetloss} %")

# b = subprocess.check_output("speedtest", shell=True).decode('utf-8')
# lines = b.split('\n')
# for li in lines:
#     if 'Download' in li:
#         down = float(li.split(' ')[1])
#     if 'Upload' in li:
#         up = float(li.split(' ')[1])

vid = pytube.YouTube(url)
print(vid.streams[0])
