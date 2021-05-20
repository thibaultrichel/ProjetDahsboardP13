import os
from tcp_latency import measure_latency
import requests
import time
from videoprops import get_video_properties
import threading

# props = get_video_properties('/Users/thibaultrichel/Desktop/COURS/PARIS/Projet P13/vidtest.mp4')
#
# print(f'''
# Codec: {props['codec_name']}
# Resolution: {props['width']}×{props['height']}
# Aspect ratio: {props['display_aspect_ratio']}
# Frame rate: {props['avg_frame_rate']}
# ''')

# url = "https://www.youtube.com/watch?v=ihJZUux8ZOQ"

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


def test():
    print('sleep 1...')
    time.sleep(1)
    print('sleep ok')


start = time.time()

thread1 = threading.Thread(target=test)
thread2 = threading.Thread(target=test)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

finish = time.time()

print(f"finished in {finish-start}")

