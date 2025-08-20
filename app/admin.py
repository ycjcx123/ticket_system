from flask import Blueprint, jsonify
from datetime import date
from decimal import Decimal
import DB
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/api/admin/dashboard')
def admin_dashboard():
    today = date.today()

    conn = DB.get_connection()
    cur = conn.cursor()

    try:
        # 1. 今日票房(今日排期的总销售额)
        cur.execute("""
            SELECT IFNULL(SUM(o.TotalAmount), 0) AS total_sales
            FROM Orders o
            JOIN Schedules s ON o.ScheduleID = s.ScheduleID  -- 显式JOIN+修正表名
            WHERE s.ScheduleDate = %s
        """, (today,))
        total_sales = cur.fetchone()['total_sales']

        # 2. 今日订单数
        cur.execute("""
            SELECT COUNT(*) AS order_count  -- 修正COUNT
            FROM Orders o
            JOIN Schedules s ON o.ScheduleID = s.ScheduleID
            WHERE s.ScheduleDate = %s
        """, (today,))
        order_count = cur.fetchone()['order_count']

        # 3. 上座率（今日已售座位 / 今日总可售座位）
        cur.execute("""
            SELECT COUNT(*) AS sold_seats
            FROM Order_Seat os
            JOIN Orders o ON os.OrderID = o.OrderID
            JOIN Schedules s ON o.ScheduleID = s.ScheduleID
            WHERE s.ScheduleDate = %s
        """, (today,))
        sold_seats = cur.fetchone()['sold_seats']
        
        # 总共可售座位
        cur.execute("""
            SELECT COUNT(*) AS total_seats  -- 从Seat表统计
            FROM Schedules s
            JOIN Seat st ON s.HallID = st.HallID  -- 关联座位表
            WHERE s.ScheduleDate = %s
        """, (today,))
        total_seats = cur.fetchone()['total_seats']

        seat_rate = (sold_seats / total_seats * 100) if total_seats > 0 else 0

        # 4. 今日排期数
        cur.execute("""
            SELECT COUNT(*) AS schedule_count
            FROM Schedules
            WHERE ScheduleDate = %s
        """, (today,))
        schedule_count = cur.fetchone()['schedule_count']

        return jsonify({
            'success': True,
            'data': {
                'total_sales': float(total_sales) if isinstance(total_sales, Decimal) else total_sales,
                'order_count': order_count,
                'seat_rate': round(seat_rate, 2),
                'schedule_count': schedule_count
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cur.close()
        conn.close()
