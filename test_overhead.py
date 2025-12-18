import os
import time
from tqdm import tqdm
import statistics

overhead_list = []

for _ in tqdm(range(100)):
    t0 = time.time()
    os.system('arecord -D plughw:CARD=sndrpihifiberry,DEV=0 -r 192000 -c 2 -f S32_LE -d 2 test.wav')
    t1 = time.time()
    
    overhead_list.append(t1-t0-2)
    time.sleep(0.5)
    
print(overhead_list)
print('min', min(overhead_list))
print('max', max(overhead_list))
print('avg', sum(overhead_list)/len(overhead_list))
print('std', statistics.stdev(overhead_list))