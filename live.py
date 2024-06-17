import requests
import re
import concurrent.futures

# 获取电视直播地址文件内容
def fetch_tv_streams(url):
    response = requests.get(url)
    response.raise_for_status()  # 确保请求成功
    return response.text

# 检查URL是否有效
def is_url_valid(url):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return url
    except requests.RequestException:
        return None
    return None

# 主函数
def main():
    source_url = "https://raw.githubusercontent.com/kimwang1978/collect-tv-txt/main/merged_output.txt"
    
    # 获取文件内容
    content = fetch_tv_streams(source_url)
    
    # 提取所有URL
    urls = re.findall(r"http://\S+", content)
    
    # 并发检查URL的有效性
    valid_urls = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(is_url_valid, url): url for url in urls}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)
    
    # 输出有效的频道信息并保存到文件
    with open("good_channels.m3u", "w") as file:
        file.write("#EXTM3U\n")
        for url in valid_urls:
            file.write(f"#EXTINF:-1,{url}\n")
            file.write(url + "\n")
            print(url)

if __name__ == "__main__":
    main()
