from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, abort
from datetime import datetime, timedelta
from ..sql.diary_db import DiaryDAO
from app.sql.achievements_db import check_achievements

diary_bp = Blueprint('diary', __name__, url_prefix="/diary")

def generate_dates(year, month):
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # 모든 날짜 리스트 생성 (정수형 일(day)만 반환)
    return [(first_day + timedelta(days=i)).day for i in range((last_day - first_day).days + 1)]

# 일기 페이지 라우트
@diary_bp.route('/')
def diary_home():
    if "user_id" not in session:
        return redirect(url_for('auth.login_user'))
    else:
        user_id = session['user_id']
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)

        # 월이 0 이하일 때: 이전 해의 12월로 이동
        if month < 1:
            year -= 1
            month = 12
        # 월이 13 이상일 때: 다음 해의 1월로 이동
        elif month > 12:
            year += 1
            month = 1

        # 해당 년월의 날짜 리스트 생성 (정수형 일(day)만 반환)
        days_in_month = generate_dates(year, month)

        diaries = DiaryDAO().get_list_diaries_with_date(user_id, year, month)       
        return render_template('diary.html', year=year, month=month, days_in_month=days_in_month, diaries=diaries)

# 특정 날짜에 대한 일기 작성 페이지 라우트
@diary_bp.route('/write/<int:day>', methods=["GET", "POST"])
def write_diary(day):
    if 'user_id' not in session:
        return redirect(url_for('auth.login_user'))
    else:
        diary_id = request.args.get('diary_id', None)
        user_id = session['user_id']
        _method = request.form.get('_method', 'upsert')

        if diary_id:
            diary = DiaryDAO().get_diary(diary_id)
            if diary['user_id'] != user_id:
                abort(403)  # 접근 권한이 없는 일기 접근 시 403 오류 발생
                current_app.logger.error(f'ERROR_LOGGING >>>  {user_id}가 다른 일기 조회 시도')
        else:
            diary = None
                        
        if request.method == 'GET':
            year = request.args.get('year', datetime.now().year, type=int)
            month = request.args.get('month', datetime.now().month, type=int)

            return render_template('write_diary.html', year=year, month=month, day=day, diary=diary)
        elif _method == "upsert":
            year = int(request.form.get('year', datetime.now().year))
            month = int(request.form.get('month', datetime.now().month))
            day = int(request.form.get('day', datetime.now().day))

            mood = request.form['mood']
            body = request.form['body']
            # file_urls = request.form['file_urls']
            formatted_date = datetime(year, month, day).strftime('%Y-%m-%d')            
            DiaryDAO().upsert_diary(user_id, mood, body, formatted_date, diary_id)

            # 업적 확인 함수 호출
            check_achievements(user_id)

            return redirect(url_for('diary.diary_home', year=year, month=month))

        elif _method == "delete":
            year = int(request.form.get('year', datetime.now().year))
            month = int(request.form.get('month', datetime.now().month))
            day = int(request.form.get('day', datetime.now().day))

            DiaryDAO().delete_diary(diary_id)
            return redirect(url_for('diary.diary_home', year=year, month=month))
