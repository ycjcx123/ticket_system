from flask import render_template, session, redirect, url_for, request, Blueprint, jsonify
import DB
from datetime import datetime, date
import pymysql
from datetime import datetime, timedelta

movie_bp = Blueprint('movie', __name__)

# 电影列表
@movie_bp.route('/api/movies')
def get_movies():
    conn = DB.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT MovieID, MovieName, MovieType, Duration, PosterPath, Director, Actors, Description FROM Movie"
            cursor.execute(sql)
            movies = cursor.fetchall()
            return jsonify(movies)
    finally:
        conn.close()

# 动态生成档期表
@movie_bp.route('/buy-ticket')
def buy_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login.show_login'))

    movie_id = request.args.get('movieID')
    if not movie_id:
        return "缺少电影ID", 400

    movie = DB.seek_movie(movie_id)
    if not movie:
        return "未找到该电影", 404

    schedules = DB.get_movie_schedules(movie_id)
    
    # 处理日期去重和格式化
    unique_dates = []
    date_set = set()
    
    for schedule in schedules:
        # 确保正确处理日期
        schedule_date = schedule['ScheduleDate']
        if isinstance(schedule_date, str):
            # 从字符串转换为date对象
            schedule_date = datetime.strptime(schedule_date, '%Y-%m-%d').date()
        elif isinstance(schedule_date, datetime):
            # 如果是datetime对象，转换为date
            schedule_date = schedule_date.date()
        
        date_key = schedule_date.strftime('%Y-%m-%d')
        if date_key not in date_set:
            date_set.add(date_key)
            
            # 计算日期文本（今天/明天/后天）
            today = date.today()  # 使用date类的today()方法
            delta = (schedule_date - today).days
            
            if delta == 0:
                day_text = "今天"
            elif delta == 1:
                day_text = "明天"
            elif delta == 2:
                day_text = "后天"
            else:
                day_text = schedule_date.strftime('%m月%d日')
            
            # 计算星期文本
            week_days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            week_text = week_days[schedule_date.weekday()]
            
            if schedule_date.weekday() >= 5:
                week_type = "休息日"
            else:
                week_type = "工作日"
                
            unique_dates.append({
                'date_str': date_key,
                'date_display': schedule_date.strftime('%m月%d日'),
                'day_text': day_text,
                'week_text': week_text,
                'week_type': week_type
            })
    
    unique_dates.sort(key=lambda x: x['date_str'])
    # print("日期数据:", unique_dates)  # 调试用
    
    return render_template('schedule.html', 
                          movie=movie, 
                          schedules=schedules,
                          unique_dates=unique_dates)

# 动态生成座位表，获取座位表信息
@movie_bp.route('/select-seats')
def choose_seats():
    """选座页面路由"""
    if 'user_id' not in session:
        return redirect(url_for('login.show_login'))

    movie_id = request.args.get('movieID')
    schedule_id = request.args.get('scheduleID')
    if not movie_id or not schedule_id:
        return "缺少电影ID或场次ID", 400

    conn = DB.get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取电影信息
            cursor.execute("SELECT * FROM Movie WHERE MovieID = %s", (movie_id,))
            movie = cursor.fetchone()

            # 获取场次信息（包括影厅）
            schedule = DB.get_schedule_seats(schedule_id)
            base_price = schedule['BasePrice']

            # 计算结束时间（在后端处理格式）
            
            if isinstance(schedule['StartTime'], timedelta):
                # 计算小时和分钟
                total_seconds = schedule['StartTime'].total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                schedule['StartTimeFormatted'] = f"{hours:02d}:{minutes:02d}"
                
                # 计算结束时间
                end_time_seconds = total_seconds + (schedule['Duration'] * 60)
                end_hours = int(end_time_seconds // 3600)
                end_minutes = int((end_time_seconds % 3600) // 60)
                schedule['EndTimeFormatted'] = f"{end_hours:02d}:{end_minutes:02d}"
            else:
                # 如果是datetime.time对象
                schedule['StartTimeFormatted'] = schedule['StartTime'].strftime('%H:%M')
                end_time = (datetime.combine(datetime.today(), schedule['StartTime']) + 
                            timedelta(minutes=schedule['Duration'])).time()
                schedule['EndTimeFormatted'] = end_time.strftime('%H:%M')

            # 格式化日期
            if isinstance(schedule['ScheduleDate'], datetime):
                schedule['ScheduleDate'] = schedule['ScheduleDate'].date()
            schedule['ScheduleDateFormatted'] = schedule['ScheduleDate'].strftime('%Y年%m月%d日')

            # 获取座位信息
            cursor.execute("""
                SELECT 
                    s.*, 
                    (sc.BasePrice + s.Price) AS ActualPrice
                FROM Seat s
                JOIN Schedules sc ON s.HallID = sc.HallID
                WHERE s.HallID = %s AND sc.ScheduleID = %s
                ORDER BY RowNumber, ColumnNumber
            """, (schedule['HallID'], schedule_id))
            seats = cursor.fetchall()
            extra_price = 10

            # 查询该场次已被占用的座位
            cursor.execute("""
                SELECT SeatID FROM Order_Seat
                WHERE ScheduleID = %s
            """, (schedule_id,))
            occupied = [row['SeatID'] for row in cursor.fetchall()]

    finally:
        conn.close()

    return render_template('seat.html',
                           movie=movie,
                           schedule=schedule,
                           seats=seats,
                           occupied_seat_ids=occupied,
                           vip_price=base_price + extra_price)

# 创建，提交订单
@movie_bp.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.get_json()
    user_id = data['userID']
    user_id = DB.mask_id(user_id)
    schedule_id = data['scheduleID']
    seats = data['seats']  # 形如 [{'seatID': 'S001', 'price': 40.0}, ...]

    order_id = DB.check_order_id()
    total_amount = sum(seat['price'] for seat in seats)
    conn = DB.get_connection()
    try:
        with conn.cursor() as cursor:
            # 插入 Orders 表
            cursor.execute("""
                INSERT INTO Orders (OrderID, UserID, ScheduleID, TotalAmount, PaymentStatus)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, user_id, schedule_id, total_amount, True))

            # 插入 Order_Seat 表
            for seat in seats:
                cursor.execute("""
                    INSERT INTO Order_Seat (OrderID, SeatID, ScheduleID, Price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, seat['seatID'], schedule_id, seat['price']))

        conn.commit()
        return jsonify({'success': True, 'orderID': order_id})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()
