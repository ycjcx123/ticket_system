import dbutils.pooled_db
import pymysql
import dbutils
from datetime import datetime
from flask import jsonify

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
    user='root',
    password='your_password',
    database='ticket_system',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

def get_connection():
    return POOL.connection()

# 格式化用户ID为10位数字，不足前面补零
def mask_id(id):
    """Format id to 10 digits by padding with leading zeros"""
    if not id:
        return id
    return id.zfill(10)

# 用户登录
def check_user(user_id, password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM Users WHERE UserID=%s AND Passwords=%s"
            mask_user_id = mask_id(user_id)
            cursor.execute(sql, (mask_user_id, password))
            return cursor.fetchone()
    finally:
        conn.close()

# 管理员登录
def check_admin(admin_id, password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM Admins WHERE AdminID=%s AND Passwords=%s"
            mask_admin_id = mask_id(admin_id)
            cursor.execute(sql, (mask_admin_id, password))
            return cursor.fetchone()
    finally:
        conn.close()

# 用户注册
def register_user(user_id, password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO Users (UserID, Passwords) VALUES (%s, %s)"
            mask_user_id = mask_id(user_id)
            cursor.execute(sql, (mask_user_id, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"注册失败：{e}")
        return False
    finally:
        conn.close()

# 判断电影是否存在
def seek_movie(movie_id):
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM movie WHERE MovieID=%s"
            cursor.execute(sql, (movie_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_movie_schedules(movie_id):
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 关联Hall表获取影厅信息
            cursor.execute(r"""
                SELECT 
                    s.ScheduleID, s.MovieID, s.HallID, s.ScheduleDate, 
                    s.StartTime, s.EndTime, s.BasePrice,
                    h.HallName, h.HallType,  # 从Hall表获取影厅名称和类型
                    c.CinemaName  # 从Cinema表获取影院名称
                FROM schedules s
                JOIN hall h ON s.HallID = h.HallID  # 关联影厅表
                JOIN cinema c ON h.CinemaID = c.CinemaID  # 通过影厅的CinemaID关联影院
                WHERE s.MovieID = %s
                ORDER BY s.ScheduleDate, s.StartTime
            """, (movie_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_schedule_seats(schedule_id):
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                    SELECT s.*, h.HallName, m.Duration
                    FROM Schedules s
                    JOIN Hall h ON s.HallID = h.HallID
                    JOIN Movie m ON s.MovieID = m.MovieID
                    WHERE s.ScheduleID = %s
                """, (schedule_id,))
            return cursor.fetchone()
    finally:
        conn.close()

# ------------创建订单-------------
def check_order_id():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(OrderID) AS max_order_id FROM Orders")
            result = cursor.fetchone()
            max_id = result['max_order_id']
            if max_id:
                new_id = int(max_id) + 1
            else:
                new_id = 1
            return str(new_id).zfill(10)
    finally:
        conn.close()

# 创建订单
def check_order_id():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(OrderID) AS max_order_id FROM Orders")
            result = cursor.fetchone()
            max_id = result['max_order_id']
            if max_id:
                new_id = int(max_id) + 1
            else:
                new_id = 1
            return str(new_id).zfill(10)
    finally:
        conn.close()

def get_halls():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT h.HallID, h.HallName, COUNT(s.SeatID) AS SeatCount
                FROM Hall h
                LEFT JOIN Seat s ON h.HallID = s.HallID
                GROUP BY h.HallID, h.HallName
            """)
            rows = cursor.fetchall()
            # halls = [dict(zip(['HallID', 'HallName', 'SeatCount'], row)) for row in rows]
            print(f"halls: {rows}")
            print(jsonify(rows))
            return rows
    finally:
        conn.close()

# get_halls()