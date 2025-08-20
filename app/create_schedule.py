from flask import render_template, session, redirect, url_for, request, Blueprint, jsonify
import DB
import pymysql
from decimal import Decimal
from datetime import date, datetime, timedelta
import logging

cs_bp = Blueprint('create_schedule', __name__)

@cs_bp.route('/create_schedule')
def check_order():
    return render_template('create_schedule.html')

# @cs_bp.route('/api/GetMovie')
# def get_movies():
#     conn = DB.get_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute("SELECT MovieID, MovieName, Duration FROM Movie")
#         movies = [dict(zip(['MovieID','MovieName','Duration'], row)) for row in cur.fetchall()]
#         return jsonify(movies)
#     finally:
#         conn.close()

@cs_bp.route('/api/movies')
def get_movies():
    conn = DB.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MovieID, MovieName, Duration FROM Movie")
    movies = [dict(zip(['MovieID','MovieName','Duration'], row)) for row in cur.fetchall()]
    print(f"movies:{movies}")
    return jsonify(movies)

@cs_bp.route('/api/halls')
def get_halls():
    conn = DB.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT h.HallID, h.HallName, COUNT(s.SeatID) AS SeatCount
        FROM Hall h
        LEFT JOIN Seat s ON h.HallID = s.HallID
        GROUP BY h.HallID, h.HallName
    """)
    # 直接转换为字典列表
    halls = [dict(row) for row in cur.fetchall()]
    # print(jsonify(halls))
    return jsonify(halls)




@cs_bp.route('/api/schedules')
def get_schedules():
    conn = DB.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.ScheduleID, s.MovieID, m.MovieName, s.HallID, h.HallName,
               s.ScheduleDate, s.StartTime, s.EndTime, s.BasePrice
        FROM Schedules s
        JOIN Movie m ON s.MovieID = m.MovieID
        JOIN Hall h ON s.HallID = h.HallID
    """)
    rows = cur.fetchall()
    
    # 转换特殊类型为JSON可序列化的格式
    schedules = []
    for row in rows:
        schedule = dict(row)  # 将行转换为字典
        
        # 转换日期对象为字符串 (YYYY-MM-DD)
        if isinstance(schedule['ScheduleDate'], date):  # 使用 date 类型
            schedule['ScheduleDate'] = schedule['ScheduleDate'].isoformat()
        
        # 转换timedelta为时间字符串 (HH:MM:SS)
        if isinstance(schedule['StartTime'], timedelta):
            total_seconds = int(schedule['StartTime'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            schedule['StartTime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        if isinstance(schedule['EndTime'], timedelta):
            total_seconds = int(schedule['EndTime'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            schedule['EndTime'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # 转换Decimal为float
        if isinstance(schedule['BasePrice'], Decimal):
            schedule['BasePrice'] = float(schedule['BasePrice'])
        
        schedules.append(schedule)
    
    # print(f"schedules: {schedules}")
    return jsonify(schedules)

@cs_bp.route('/api/schedules/save', methods=['POST'])
def save_schedules():
    data = request.json
    added = data.get('added', [])
    modified = data.get('modified', [])
    removed = data.get('removed', [])
    
    conn = DB.get_connection()
    cur = conn.cursor()
    response_data = {'success': True, 'message': '', 'addedIds': []}
    
    try:
        # 1. 处理删除
        for schedule_id in removed:
            cur.execute("DELETE FROM Schedules WHERE ScheduleID = %s", (schedule_id,))
        
        # 2. 处理修改（关键修改：更新影厅ID）
        for item in modified:
            cur.execute("""
                UPDATE Schedules 
                SET StartTime = %s, EndTime = %s, BasePrice = %s, HallID = %s
                WHERE ScheduleID = %s
            """, (item['startTime'], item['endTime'], item['basePrice'], item['hallId'], item['scheduleId']))
        # 3. 处理新增
        for item in added:
            # 生成新ID (SC + 8位数字)
            cur.execute("SELECT MAX(ScheduleID) AS max_id FROM Schedules")
            row = cur.fetchone()

            if row:
                # 如果是 dict cursor
                max_id = row['max_id'] if isinstance(row, dict) else row[0]
            else:
                max_id = None

            if max_id:
                try:
                    new_num = int(max_id[2:]) + 1
                except ValueError:
                    raise ValueError(f"现有 ScheduleID 格式错误: {max_id}")
                new_id = f"SC{new_num:08d}"
            else:
                new_id = "SC00000001"

            print("MAX ScheduleID from DB:", max_id)
            print("Generated new_id:", new_id)

            # 插入新记录
            cur.execute("""
                INSERT INTO Schedules (ScheduleID, MovieID, HallID, ScheduleDate, StartTime, EndTime, BasePrice)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                new_id,
                item['movieId'],
                item['hallId'],
                item['scheduleDate'],
                item['startTime'],
                item['endTime'],
                item['basePrice']
            ))
            
            # 记录ID映射
            response_data['addedIds'].append({
                'tempId': item.get('tempId', ''),  # 前端传递的临时ID
                'newId': new_id
            })
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        response_data['success'] = False
        response_data['message'] = str(e)
        logging.error(f"保存排期失败: {str(e)}")
        print("保存排期失败:", repr(e))
    finally:
        cur.close()
        conn.close()
    
    return jsonify(response_data)