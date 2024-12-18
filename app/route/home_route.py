from flask import Blueprint, render_template, session, redirect, url_for

# 홈 페이지 블루프린트 생성
home_bp = Blueprint('home', __name__)

# 홈 페이지 라우트 정의
@home_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('diary.diary_home'))
    else:
        # 로그인되지 않은 경우 로그인 페이지로 리다이렉트
        return redirect(url_for('auth.login_user'))