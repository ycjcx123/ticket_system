from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
from DB import check_user, check_admin, register_user

login_bp = Blueprint('login', __name__)

@login_bp.route('/')
def show_login():
    return render_template('login.html')


# 用户登录接口
@login_bp.route('/user/home')
def show_user():
    if 'user_id' not in session:
        return redirect(url_for('login.show_login'))
    
    userid = session['user_id']
    return render_template('user.html', userid=userid)


# 用户登录接口
@login_bp.route('/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    userid = data.get('userid')
    password = data.get('password')
    user = check_user(userid, password)
    if user:
        session.clear()  # 清空所有 session
        session['user_id'] = userid
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    

# 管理员登录接口
@login_bp.route('/admin/home')
def show_admin():
    if 'admin_id' not in session:
        return redirect(url_for('login.show_login'))
    
    adminid = session['admin_id']
    return render_template('admin.html', adminid=adminid)

# 管理员登录接口
@login_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    adminid = data.get('adminId')
    password = data.get('adminPassword')
    admin = check_admin(adminid, password)
    if admin:
        session.clear()  # 清空所有 session
        session['admin_id'] = adminid
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

# 用户注册
@login_bp.route('/user/register', methods=['POST'])
def user_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    success = register_user(username, password)
    return jsonify({'success': success})

# 用户登出
@login_bp.route('/logout')
def logout():
    session.pop('user_id', None)  # 清除 session
    return redirect(url_for('login.show_login'))  # 回到登录页

