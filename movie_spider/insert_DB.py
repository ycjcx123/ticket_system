import pymysql
import json
import dbutils.pooled_db

POOL = dbutils.pooled_db.PooledDB(
    creator=pymysql,
    maxconnections=10,  
    mincached = 2,        
    maxcached = 5,        
    maxshared = 3,      
    blocking = True,
    setsession = [],
    ping = 0,

    host='127.0.0.1',
    port=3306,
    user='root',   # 数据库用户名
    password='your_password',   # 数据库密码
    database='ticket_system',   #数据库名
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

def get_connection():
    return POOL.connection()

# 插入电影
def insert_movie():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            data_path = "E:/DataBase/movie/movie_data.json"
            
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                insert_query = """
                INSERT INTO Movie (
                    MovieID, MovieName, MovieType, Duration, 
                    PosterPath, Director, Actors, Description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # 准备所有数据
                movies_to_insert = []
                for movie in raw_data:
                    # 生成固定长度的MovieID：前缀"Mov" + 9位数字（不足补0）
                    movie_id = "Mov" + str(movie["id"]).zfill(7)
                    
                    data = (
                        movie_id,                
                        movie["title"],          
                        movie["type"],           
                        movie["duration"],       
                        movie["poster"],         
                        movie["director"],       
                        movie["actors"],         
                        movie["desc"]            
                    )
                    movies_to_insert.append(data)
                
                # 批量执行插入
                cursor.executemany(insert_query, movies_to_insert)
                conn.commit()
                print(f"成功插入 {len(movies_to_insert)} 条记录")
                
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                conn.rollback()
            except pymysql.Error as e:
                print(f"数据库错误: {e}")
                conn.rollback()
            except Exception as e:
                print(f"未知错误: {e}")
                conn.rollback()

# 插入影厅
def insert_hall():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # 使用双引号且英文逗号的合法JSON
                hall_data = '''[
                    {
                        "HallID": "H000000001",
                        "HallName": "一号厅",
                        "HallType": "激光厅",
                        "CinemaID": "0000000001"
                    },
                    {
                        "HallID": "H000000002",
                        "HallName": "二号厅",
                        "HallType": "激光厅",
                        "CinemaID": "0000000001"
                    },
                    {
                        "HallID": "H000000003",
                        "HallName": "三号厅",
                        "HallType": "激光厅",
                        "CinemaID": "0000000001"
                    },
                    {
                        "HallID": "H000000004",
                        "HallName": "四号厅",
                        "HallType": "激光厅",
                        "CinemaID": "0000000001"
                    },
                    {
                        "HallID": "H000000005",
                        "HallName": "五号厅",
                        "HallType": "激光厅",
                        "CinemaID": "0000000001"
                    },
                    {
                        "HallID": "H000000006",
                        "HallName": "巨幕厅",
                        "HallType": "中国巨幕",
                        "CinemaID": "0000000001"
                    },
                    {
                        "HallID": "H000000007",
                        "HallName": "IMAX",
                        "HallType": "IMAX",
                        "CinemaID": "0000000001"
                    },
                    {
                        "HallID": "H000000008",
                        "HallName": "杜比全景声",
                        "HallType": "杜比全景声",
                        "CinemaID": "0000000001"
                    }
                ]'''
                

                # 解析JSON字符串为Python对象
                data = json.loads(hall_data)
                
                # 修复SQL语法：去掉多余的逗号
                insert_query = """
                INSERT INTO Hall (
                    HallID, HallName, HallType, CinemaID
                ) VALUES (%s, %s, %s, %s)
                """
                
                # 准备所有数据
                hall_to_insert = []
                for hall in data:              
                    data = (
                        hall["HallID"],                
                        hall["HallName"],          
                        hall["HallType"],           
                        hall["CinemaID"]                 
                    )
                    hall_to_insert.append(data)
                
                # 批量执行插入
                cursor.executemany(insert_query, hall_to_insert)
                conn.commit()
                print(f"成功插入 {len(hall_to_insert)} 条记录")
                
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                conn.rollback()
            except pymysql.Error as e:
                print(f"数据库错误: {e}")
                conn.rollback()
            except Exception as e:
                print(f"未知错误: {e}")
                conn.rollback()

# 插入座位，rows和cols分别表示影厅的行数和列数，aim_hall表示影厅的ID
def insert_seat(rows, cols, aim_hall):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # 步骤1: 获取当前最大的SeatID
            cursor.execute("SELECT MAX(CAST(SUBSTRING(SeatID, 2) AS UNSIGNED)) AS max_id FROM Seat")
            result = cursor.fetchone()
            current_max_id = result['max_id'] if result['max_id'] is not None else 0
            next_seat_id = current_max_id + 1
            print(next_seat_id)
            
            vip_col_start = int(cols / 3) + 1
            vip_col_end = int(cols * 2 / 3)

            vip_row_start = int(rows / 3) + 1
            vip_row_end = int(rows * 2 / 3)

            seat_data = []
            for row in range(1, rows + 1):
                for col in range(1, cols + 1):
                    # 确定座位类型和价格
                    if vip_row_start <= row <= vip_row_end and vip_col_start <= col <= vip_col_end:
                        seat_type = "vip"
                        price = 10.00
                    else:
                        seat_type = "普通"
                        price = 0.00
                    
                    # 生成SeatID（格式：S000000001）
                    seat_id = f"{next_seat_id}".zfill(10)
                    next_seat_id += 1
                    
                    # 添加到数据列表
                    seat_data.append((seat_id, aim_hall, row, col, seat_type, price))
            insert_query = """
                INSERT INTO Seat (SeatID, HallID, RowNumber, ColumnNumber, SeatType, Price)
                VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.executemany(insert_query, seat_data)
            conn.commit()
            print(f"成功插入 {len(seat_data)} 个座位到数据库")