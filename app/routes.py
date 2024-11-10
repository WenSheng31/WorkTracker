from flask import render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime, timedelta, time
from calendar import monthrange
from . import db
from .models import WorkHours, Settings

# 午休時間
LUNCH_START = time(12, 0)
LUNCH_END = time(13, 0)


def login_required(f):
    """確保使用者已登入"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def calculate_work_hours(start_dt, end_dt):
    """計算工作時數，自動扣除午休時間"""
    # 處理跨日情況
    if end_dt < start_dt:
        end_dt += timedelta(days=1)

    total_hours = (end_dt - start_dt).total_seconds() / 3600

    # 處理午休時間
    lunch_start_dt = datetime.combine(start_dt.date(), LUNCH_START)
    lunch_end_dt = datetime.combine(start_dt.date(), LUNCH_END)

    # 如果工作時間橫跨午休時間，扣除一小時
    if start_dt <= lunch_end_dt and end_dt >= lunch_start_dt:
        total_hours -= 1

    # 如果跨日且第二天也橫跨午休時間
    if end_dt.date() > start_dt.date():
        next_lunch_start = lunch_start_dt + timedelta(days=1)
        next_lunch_end = lunch_end_dt + timedelta(days=1)
        if start_dt <= next_lunch_end and end_dt >= next_lunch_start:
            total_hours -= 1

    return round(total_hours, 2)


def get_monthly_records(year, month):
    """獲取指定月份的工時記錄和統計"""
    # 獲取月份的起始和結束日期
    _, last_day = monthrange(year, month)
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, last_day).date()

    # 查詢該月的工時記錄
    records = WorkHours.query.filter(
        WorkHours.date >= start_date,
        WorkHours.date <= end_date
    ).order_by(WorkHours.date.desc()).all()

    # 計算總工時
    total_hours = sum(record.hours for record in records)

    # 計算總薪資
    settings = Settings.query.first()
    hourly_rate = settings.hourly_rate if settings else 0
    total_salary = total_hours * hourly_rate

    return records, total_hours, total_salary


def register_routes(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            password = request.form.get('password')
            settings = Settings.query.first()
            if settings and password == settings.password:
                session['logged_in'] = True
                return redirect(url_for('index'))
            flash('密碼錯誤')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def index():
        # 獲取當前年月或從URL參數獲取
        current_date = datetime.now()
        year = int(request.args.get('year', current_date.year))
        month = int(request.args.get('month', current_date.month))

        # 獲取月份記錄和統計
        work_hours, total_hours, total_salary = get_monthly_records(year, month)

        # 計算上個月和下個月的日期
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        return render_template('index.html',
                               year=year,
                               month=month,
                               prev_year=prev_year,
                               prev_month=prev_month,
                               next_year=next_year,
                               next_month=next_month,
                               work_hours=work_hours,
                               total_hours=total_hours,
                               total_salary=total_salary)

    @app.route('/add', methods=['POST'])
    @login_required
    def add_hours():
        try:
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
            end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()

            # 計算工時
            start_dt = datetime.combine(date, start_time)
            end_dt = datetime.combine(date, end_time)
            hours = calculate_work_hours(start_dt, end_dt)

            # 驗證工時
            if hours <= 0:
                flash('工時必須大於0小時')
                return redirect(url_for('index'))
            if hours > 24:
                flash('工時不能超過24小時')
                return redirect(url_for('index'))

            # 創建記錄
            work_hours = WorkHours(
                date=date,
                start_time=start_time,
                end_time=end_time,
                hours=hours
            )
            db.session.add(work_hours)
            db.session.commit()
            flash('工時記錄已新增')

        except Exception as e:
            flash(f'新增記錄時發生錯誤: {str(e)}')

        return redirect(url_for('index', year=date.year, month=date.month))

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_hours(id):
        record = WorkHours.query.get_or_404(id)

        if request.method == 'POST':
            try:
                date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
                start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
                end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()

                # 計算工時
                start_dt = datetime.combine(date, start_time)
                end_dt = datetime.combine(date, end_time)
                hours = calculate_work_hours(start_dt, end_dt)

                # 驗證工時
                if hours <= 0 or hours > 24:
                    flash('請確認工時是否正確')
                    return redirect(url_for('edit_hours', id=id))

                # 更新記錄
                record.date = date
                record.start_time = start_time
                record.end_time = end_time
                record.hours = hours

                db.session.commit()
                flash('工時記錄已更新')
                return redirect(url_for('index', year=date.year, month=date.month))

            except Exception as e:
                flash(f'更新記錄時發生錯誤: {str(e)}')
                return redirect(url_for('edit_hours', id=id))

        return render_template('edit_hours.html', record=record)

    @app.route('/delete/<int:id>', methods=['POST'])
    @login_required
    def delete_hours(id):
        try:
            record = WorkHours.query.get_or_404(id)
            year = record.date.year
            month = record.date.month
            db.session.delete(record)
            db.session.commit()
            flash('工時記錄已刪除')
            return redirect(url_for('index', year=year, month=month))
        except Exception as e:
            flash(f'刪除記錄時發生錯誤: {str(e)}')
            return redirect(url_for('index'))

    @app.route('/settings', methods=['GET', 'POST'])
    @login_required
    def settings():
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()

        if request.method == 'POST':
            try:
                hourly_rate = float(request.form['hourly_rate'])
                if hourly_rate < 0:
                    flash('時薪不能為負數')
                    return redirect(url_for('settings'))

                settings.hourly_rate = hourly_rate
                if request.form['new_password']:
                    settings.password = request.form['new_password']

                db.session.commit()
                flash('設定已更新')

            except ValueError:
                flash('請輸入有效的時薪金額')
            except Exception as e:
                flash(f'更新設定時發生錯誤: {str(e)}')

            return redirect(url_for('settings'))

        return render_template('settings.html', settings=settings)

    return app
