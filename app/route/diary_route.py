from flask import *
from datetime import datetime, timedelta
from ..sql.diary_db import DiaryDAO

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
    # GET 요청에서 연도와 월을 가져옵니다.
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

    return render_template('diary.html', year=year, month=month, days_in_month=days_in_month)

# 특정 날짜에 대한 일기 작성 페이지 라우트
@diary_bp.route('/write/<day>', methods=["DELETE", "GET", "POST"])
def write_diary(day):
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    if request.method == "GET":            
        return render_template('write_diary.html', year=year, month=month, day=day)
    elif request.method == "POST":
        # 날짜 포맷팅
        formatted_date = datetime(year, month, day).strftime('%Y-%m-%d')
        
        DiaryDAO().upsert_diary()
    else:
        return

        

@diary_bp.route('/<int:year>/<int:month>')
def get_diaries(year, month):
    days_in_month = [day for day in range(1, 32)]

    diaries = DiaryDAO().get_list_diaries_with_date(year, month)
    
    return render_template(
        'diary.html',
        year=year,
        month=month,
        days_in_month=days_in_month,
        diaries=diaries
    )