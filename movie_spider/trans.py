import json
import re
import os

def transform_movies(raw_data):
    """转换电影数据格式的函数"""
    transformed = []
    for idx, movie in enumerate(raw_data, 1):
        # 提取时长中的数字并转为整数
        duration_match = re.search(r'\d+', movie["duration"])
        duration = int(duration_match.group()) if duration_match else 0
        
        # 构建新的海报路径（使用标题作为文件名）
        poster_path = f"static/movie_images/{movie['title']}.jpg"
        
        transformed.append({
            "id": idx,
            "title": movie["title"],
            "poster": poster_path,
            "type": "",  # 保留空字段
            "duration": duration,
            "director": movie["director"],
            "actors": ", ".join(movie["actors"]),  # 数组转字符串
            "desc": ""   # 保留空字段
        })
    return transformed

# 主处理流程
if __name__ == "__main__":
    input_file = "E:/DataBase/movie/movies_data_org.json"        # 输入文件名
    output_file = "E:/DataBase/movie/movies_data.json"  # 输出文件名
    
    # 1. 读取原始JSON文件
    if not os.path.exists(input_file):
        print(f"错误：文件 {input_file} 不存在！")
        exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 2. 转换数据
    try:
        transformed_data = transform_movies(raw_data)
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        exit(1)
    
    # 3. 保存转换后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, ensure_ascii=False, indent=4)
    
    print(f"转换成功！已保存到 {output_file}")
    print(f"共转换 {len(transformed_data)} 条电影数据")