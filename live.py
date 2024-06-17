import time
import concurrent.futures
import requests
import re
import os
import threading
from queue import Queue
from datetime import datetime
import eventlet

# Function to modify URLs for all possible IP addresses in the range
def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)
    return modified_urls

# Function to check if a URL is accessible
def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

# Get the page content from the provided URL
source_url = "https://raw.bgithub.xyz/kimwang1978/collect-tv-txt/main/merged_output.txt"
response = requests.get(source_url)
page_content = response.text

# Find all URLs matching the specified pattern
pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
urls_all = re.findall(pattern, page_content)
urls = set(urls_all)

# Create new URLs with modified IP addresses
x_urls = []
for url in urls:
    url = url.strip()
    ip_start_index = url.find("//") + 2
    ip_dot_three = url.rfind(".", 0, url.find(":")) + 1
    base_url = url[:ip_start_index]
    ip_address = url[ip_start_index:ip_dot_three]
    port = url[url.find(":", ip_start_index):]
    modified_ip = f"{ip_address}1"
    x_url = f"{base_url}{modified_ip}{port}"
    x_urls.append(x_url)
urls = set(x_urls)

# Check the accessibility of the modified URLs
valid_urls = []
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futures = []
    for url in urls:
        url = url.strip()
        modified_urls = modify_urls(url)
        for modified_url in modified_urls:
            futures.append(executor.submit(is_url_accessible, modified_url))
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            valid_urls.append(result)

# Process valid URLs to extract channel information
results = []
for url in valid_urls:
    try:
        ip_start_index = url.find("//") + 2
        ip_index_second = url.find("/", ip_start_index + 3)
        base_url = url[:ip_start_index]
        ip_address = url[ip_start_index:ip_index_second]
        url_x = f"{base_url}{ip_address}"
        json_url = url
        response = requests.get(json_url, timeout=0.5)
        json_data = response.json()

        for item in json_data['data']:
            if isinstance(item, dict):
                name = item.get('name')
                urlx = item.get('url')
                if ',' in urlx:
                    urlx = "aaaaaaaa"
                if 'http' in urlx:
                    urld = urlx
                else:
                    urld = f"{url_x}{urlx}"
                if name and urld:
                    name = name.replace("中央", "CCTV").replace("高清", "").replace("HD", "").replace("标清", "")
                    name = name.replace("超高", "").replace("频道", "").replace("-", "").replace(" ", "")
                    name = name.replace("PLUS", "+").replace("＋", "+").replace("(", "").replace(")", "")
                    name = name.replace("L", "").replace("CMIPTV", "").replace("cctv", "CCTV")
                    name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                    name = name.replace("CCTV1综合", "CCTV1").replace("CCTV2财经", "CCTV2")
                    name = name.replace("CCTV3综艺", "CCTV3").replace("CCTV4国际", "CCTV4")
                    name = name.replace("CCTV4中文国际", "CCTV4").replace("CCTV4欧洲", "CCTV4")
                    name = name.replace("CCTV5体育", "CCTV5").replace("CCTV5+体育", "CCTV5+")
                    name = name.replace("CCTV6电影", "CCTV6").replace("CCTV7军事", "CCTV7")
                    name = name.replace("CCTV7军农", "CCTV7").replace("CCTV7农业", "CCTV7")
                    name = name.replace("CCTV7国防军事", "CCTV7").replace("CCTV8电视剧", "CCTV8")
                    name = name.replace("CCTV8纪录", "CCTV9").replace("CCTV9记录", "CCTV9")
                    name = name.replace("CCTV9纪录", "CCTV9").replace("CCTV10科教", "CCTV10")
                    name = name.replace("CCTV11戏曲", "CCTV11").replace("CCTV12社会与法", "CCTV12")
                    name = name.replace("CCTV13新闻", "CCTV13").replace("CCTV新闻", "CCTV13")
                    name = name.replace("CCTV14少儿", "CCTV14").replace("央视14少儿", "CCTV14")
                    name = name.replace("CCTV少儿超", "CCTV14").replace("CCTV15音乐", "CCTV15")
                    name = name.replace("CCTV音乐", "CCTV15").replace("CCTV16奥林匹克", "CCTV16")
                    name = name.replace("CCTV17农业农村", "CCTV17").replace("CCTV17军农", "CCTV17")
                    name = name.replace("CCTV17农业", "CCTV17").replace("CCTV5+体育赛视", "CCTV5+")
                    name = name.replace("CCTV5+赛视", "CCTV5+").replace("CCTV5+体育赛事", "CCTV5+")
                    name = name.replace("CCTV5+赛事", "CCTV5+").replace("CCTV5+体育", "CCTV5+")
                    name = name.replace("CCTV5赛事", "CCTV5+").replace("凤凰中文台", "凤凰中文")
                    name = name.replace("凤凰资讯台", "凤凰资讯").replace("CCTV4K测试）", "CCTV4")
                    name = name.replace("CCTV164K", "CCTV16").replace("上海东方卫视", "上海卫视")
                    name = name.replace("东方卫视", "上海卫视").replace("内蒙卫视", "内蒙古卫视")
                    name = name.replace("福建东南卫视", "东南卫视").replace("广东南方卫视", "南方卫视")
                    name = name.replace("金鹰卡通卫视", "金鹰卡通").replace("湖南金鹰卡通", "金鹰卡通")
                    name = name.replace("炫动卡通", "哈哈炫动").replace("卡酷卡通", "卡酷少儿")
                    name = name.replace("卡酷动画", "卡酷少儿").replace("BRTVKAKU少儿", "卡酷少儿")
                    name = name.replace("优曼卡通", "优漫卡通").replace("嘉佳卡通", "佳嘉卡通")
                    name = name.replace("世界地理", "地理世界").replace("CCTV世界地理", "地理世界")
                    name = name.replace("BTV北京卫视", "北京卫视").replace("BTV冬奥纪实", "冬奥纪实")
                    name = name.replace("东奥纪实", "冬奥纪实").replace("卫视台", "卫视")
                    name = name.replace("湖南电视台", "湖南卫视").replace("少儿科教", "少儿")
                    name = name.replace("影视剧", "影视")
                    results.append(f"{name},{urld}")
    except:
        continue

# Write all results to a file
channels = []
for result in results:
    line = result.strip()
    if result:
        channel_name, channel_url = result.split(',')
        channels.append((channel_name, channel_url))

with open("iptv.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)

eventlet.monkey_patch()

def test_url(url):
    try:
        with eventlet.Timeout(10):
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "video" in content_type:
                    return url, True
            return url, False
    except:
        return url, False

queue = Queue()
result_lock = threading.Lock()
good_channels = []
bad_channels = []

def worker():
    while True:
        channel_name, channel_url = queue.get()
        if channel_url is None:
            break
        url, status = test_url(channel_url)
        with result_lock:
            if status:
                good_channels.append((channel_name, channel_url))
                print(f"GOOD {channel_name} - {channel_url}")
            else:
                bad_channels.append((channel_name, channel_url))
                print(f"BAD {channel_name} - {channel_url}")
        queue.task_done()

for _ in range(10):
    threading.Thread(target=worker).start()

for channel_name, channel_url in channels:
    queue.put((channel_name, channel_url))

queue.join()

for _ in range(10):
    queue.put((None, None))

now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")
with open("good_channels.m3u", "w", encoding='utf-8') as file:
    file.write("#EXTM3U\n")
    for channel_name, channel_url in good_channels:
        file.write(f"#EXTINF:-1,{channel_name}\n{channel_url}\n")
