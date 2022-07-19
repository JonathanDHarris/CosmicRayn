import time, sys, argparse
import pygame
import csv
import numpy as np
import requests
from requests.structures import CaseInsensitiveDict

#https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def fetch_data():
    # https://reqbin.com/
    print("Fetching data...")
    url = "http://cosray.phys.uoa.gr/apps/algComp/formlibrary/formLoader.php"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    headers["Accept-Language"] = "en-GB,en-US;q=0.9,en;q=0.8"
    headers["Cache-Control"] = "max-age=0"
    headers["Connection"] = "keep-alive"
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Cookie"] = "18a2cf34d88162b2af250ad922198e38=be82da6d7e0badcfc02540b3b0cfebf8; offlajn-accordion-106-1-off-nav-507=1"
    headers["Origin"] = "http://cosray.phys.uoa.gr"
    headers["Referer"] = "http://cosray.phys.uoa.gr/apps/algComp/form.html"
    headers["Sec-GPC"] = "1"
    headers["Upgrade-Insecure-Requests"] = "1"
    headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"

    data = "period=1+Day&now=now&source1=15&source2=0&output=2"

    resp = requests.post(url, headers=headers, data=data)

    content = resp.content
    print("Success")
    return content.decode("utf-8").split('\r\n')
 
def get_percentiles(counts):
    count_percentiles = []

    if verbose:
        print("percentiles")
    for percentile in percentiles:
        count_percentile = np.percentile(counts, percentile)
        count_percentiles.append(count_percentile)
        if verbose:
            print(count_percentile)
            
    print("min:", min(counts))
    print("max:",max(counts))
    return count_percentiles
 
if __name__ == "__main__":
    parser=argparse.ArgumentParser()

    parser.add_argument('--stream', help='Live stream data, default True')
    parser.add_argument('--verbose', help='Verbose logging, default False')


    args = parser.parse_args()
    stream = args.stream != 'False'
    verbose = args.verbose == 'True'
        
    pygame.mixer.init()
    # https://www.videvo.net/sound-effect/rain-fall-medium-pe1005201/254265/
    sound_file = 'RainFallMedium PE1005201.mp3'
    sound = pygame.mixer.Sound(sound_file)

    counts = []        

    percentiles = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100]

    volume = 0.
    sound.set_volume(volume)

    sound.play(loops=-1)

    sleep_time = 0.1
    volume_increment = 0.01
    target_volume = 0.

    if not stream:
        data_file = '1656616659_Athens_CosRay_Data.txt'

        with open(data_file, newline='') as cfile:
            lines = cfile.readlines()
            for i in range(6,len(lines)):
                row = lines[i]
                if verbose:
                    print("row:",row)
                try:
                    count = float(row.split('\t')[-1])
                    counts.append(count)
                    if verbose:
                        print(count)
                except:
                    print("Unable to parse row")
                    print(row)

        count_percentiles = get_percentiles(counts)
    
        count_idx = -1
        while count_idx < len(counts):
            count_idx += 1
            count = counts[count_idx]
            nearest_count_percentile = find_nearest(count_percentiles, count)
            nearest_count_percentile_idx = count_percentiles.index(nearest_count_percentile)
            target_volume = percentiles[nearest_count_percentile_idx] * 0.01
            print("===")
            print("count: ", count, nearest_count_percentile, percentiles[nearest_count_percentile_idx])
            print("target_volume: ", target_volume)
            
            second = 0
            
            while second < 60:
                second += sleep_time
                if volume < target_volume:
                    volume += volume_increment
                    if volume > target_volume:
                        volume = target_volume
                    if verbose:
                        print("volume: ", volume)
                if volume > target_volume:
                    volume -= volume_increment
                    if volume < target_volume:
                        volume = target_volume
                    if verbose:
                        print("volume: ", volume)

                sound.set_volume(volume)
                time.sleep(sleep_time)
    else:
        print("Streaming...")
        lines = fetch_data()
        print("Getting percentiles")
        first_count_idx = 100
        if len(lines)-9 < first_count_idx:
            first_count_idx=len(lines)-6
        for i in range(first_count_idx, len(lines)-3):
            try:
                counts.append(float(lines[i].split(' ')[-1].split('\t')[-1]))
            except:
                print("Could not parse count")
        count_percentiles = get_percentiles(counts)
        print(count_percentiles)
        print("...done")
        
        while True:
            lines = fetch_data()
            try:
                count = float(lines[-3].split(' ')[-1].split('\t')[-1])
                nearest_count_percentile = find_nearest(count_percentiles, count)
                nearest_count_percentile_idx = count_percentiles.index(nearest_count_percentile)
                target_volume = percentiles[nearest_count_percentile_idx] * 0.01
                print("count: ", count, nearest_count_percentile, percentiles[nearest_count_percentile_idx])
                print("target_volume: ", target_volume)
            except:
                print("Could not parse data")
            
            while volume != target_volume:
                if volume < target_volume:
                    volume += volume_increment
                    if volume > target_volume:
                        volume = target_volume
                    if verbose:
                        print("volume: ", volume)
                if volume > target_volume:
                    volume -= volume_increment
                    if volume < target_volume:
                        volume = target_volume
                    if verbose:
                        print("volume: ", volume)

                sound.set_volume(volume)
                time.sleep(sleep_time)
            if verbose:
                print("Sleep 20 seconds...")
            time.sleep(20)

    print('end')
