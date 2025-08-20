from DB import get_connection, mask_id
from flask import jsonify, request, session, Blueprint, render_template

order_bp = Blueprint('orders', __name__)


@order_bp.route('/check_order')
def check_order():
    return render_template('order.html')


@order_bp.route('/api/orders')
def get_orders():
    # 登录校验
    if 'user_id' not in session and 'admin_id' not in session:
        return jsonify({"error": "未登录"}), 401

    role = 'admin' if 'admin_id' in session else 'user'
    conn = get_connection()

    def row_to_letter(row_num):
        return chr(ord('A') + row_num - 1)

    # 搜索条件
    search_uid = request.args.get('user_id')
    search_oid = request.args.get('order_id')

    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                o.OrderID AS id,
                o.UserID AS user_id,
                DATE(o.PurchaseTime) AS date,
                m.MovieName AS movie,
                CONCAT(s.ScheduleDate, ' ', s.StartTime) AS time,
                h.HallName AS hall,
                GROUP_CONCAT(seat.RowNumber ORDER BY seat.RowNumber, seat.ColumnNumber) AS seat_rows,
                GROUP_CONCAT(seat.ColumnNumber ORDER BY seat.RowNumber, seat.ColumnNumber) AS seat_cols,
                o.TotalAmount AS price,
                CASE 
                    WHEN o.PaymentStatus = 1 THEN '已完成'
                    ELSE '未支付'
                END AS status
            FROM Orders o
            LEFT JOIN Schedules s ON o.ScheduleID = s.ScheduleID
            LEFT JOIN Movie m ON s.MovieID = m.MovieID
            LEFT JOIN Hall h ON s.HallID = h.HallID
            LEFT JOIN Order_Seat os ON o.OrderID = os.OrderID AND o.ScheduleID = os.ScheduleID
            LEFT JOIN Seat seat ON os.SeatID = seat.SeatID
            WHERE 1=1
            """

            params = []

            if role == 'user':
                sql += " AND o.UserID = %s"
                params.append(mask_id(session['user_id']))
            else:
                if search_uid:
                    sql += " AND o.UserID = %s"
                    params.append(mask_id(search_uid))
                if search_oid:
                    sql += " AND o.OrderID = %s"
                    params.append(search_oid)

            sql += " GROUP BY o.OrderID ORDER BY o.PurchaseTime DESC"
            cursor.execute(sql, tuple(params))
            orders = cursor.fetchall()

            # 数据转换
            for o in orders:
                o['date'] = o['date'].strftime("%Y-%m-%d")
                if o['seat_rows'] and o['seat_cols']:
                    rows = list(map(int, o['seat_rows'].split(',')))
                    cols = list(map(int, o['seat_cols'].split(',')))
                    o['seats'] = [f"{row_to_letter(r)}{c}" for r, c in zip(rows, cols)]
                else:
                    o['seats'] = []
                o['price'] = float(o['price'])
                del o['seat_rows']
                del o['seat_cols']

            return jsonify({"role": role, "orders": orders})
    finally:
        conn.close()

@order_bp.route('/api/delete_order',methods=['DELETE'])
def delete_order():
    # 登录校验
    if 'user_id' not in session and 'admin_id' not in session:
        return jsonify({"error": "未登录"}), 401

    role = 'admin' if 'admin_id' in session else 'user'
    if role == 'user':
        return jsonify({"error": "无权限"}), 403
    
    order_id = request.args.get('orderID')
    if not order_id:
        return jsonify({"success": False, "message": "缺少订单ID"}), 400
    
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Order_Seat WHERE OrderID = %s", (order_id,))
            cursor.execute("DELETE FROM Orders WHERE OrderID = %s", (order_id,))
        conn.commit()
        return jsonify({"success": True, "message": "删除成功"})

    finally:
        conn.close()

    