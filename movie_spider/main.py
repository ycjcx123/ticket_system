import re
import requests
import os
import json
from datetime import datetime

# 爬取豆瓣的电影信息
url = "https://movie.douban.com/cinema/nowplaying/"

# 这是猫眼的
# url = "https://www.maoyan.com/films?showType=1"
headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
}
response = requests.get(url, headers=headers)

page_text = response.text

# 这是爬取豆瓣的
obj = re.compile(r'<li.*?data-title="(?P<title>.*?)".*?data-duration="(?P<duration>.*?)".*?data-director="(?P<director>.*?)".*?data-actors="(?P<actors>.*?)".*?<li class="poster">.*?<img src="(?P<images>.*?)"', re.S)

# 这是猫眼的
# obj = re.compile(r'<div class="movie-item-hover">.*?<img class="movie-hover-img" src="(?P<images>.*?)".*?<span class="name ">(?P<name>.*?)</span>.*?<span class="hover-tag">类型:</span>(?P<type>.*?)</div>.*?<span class="hover-tag">主演:</span>(?P<actors>.*?)</div>', re.S)


result = obj.findall(page_text)


# 创建保存目录
image_dir = "movie_images"
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# 处理每部电影
movies_data = []
for item in result:
    title, duration, director, actors, image_url = item
    
    # 保存图片
    try:
        img_data = requests.get(image_url, headers=headers).content
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')) # 电影名.jpg
        filename = f"{safe_title}.jpg"
        filepath = os.path.join(image_dir, filename)
        
        with open(filepath, 'wb') as img_file:
            img_file.write(img_data)
    except Exception as e:
        print(f"封面下载失败: {title} - {str(e)}")
        filepath = None
    
    # 构建电影数据
    movie = {
        "title": title,
        "duration": duration,
        "director": director,
        "actors": [a.strip() for a in actors.split('/')],
        "image_url": image_url,
        "local_image": filepath if filepath else None
    }
    movies_data.append(movie)

# 5. 保存为JSON
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
json_filename = f"movies_data_{timestamp}.json"

with open(json_filename, 'w', encoding='utf-8') as json_file:
    json.dump(movies_data, json_file, ensure_ascii=False, indent=2)

print(f"爬取完成! 共处理 {len(movies_data)} 部电影")
print(f"图片保存在: {image_dir}/")
print(f"数据保存在: {json_filename}")