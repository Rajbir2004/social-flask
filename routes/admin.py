from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Post, Report, Notification
from datetime import datetime, timezone, timedelta

admin_bp = Blueprint('admin', __name__)

def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

@admin_bp.route('/admin')
@login_required
def dashboard():
    admin_required()
    total_users = User.query.count()
    total_posts = Post.query.count()
    
    # Active users in last 24h
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    active_users = User.query.filter(User.last_seen >= one_day_ago).count()
    
    recent_reports = Report.query.filter_by(resolved=False).order_by(Report.timestamp.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           total_users=total_users, 
                           total_posts=total_posts, 
                           active_users=active_users,
                           recent_reports=recent_reports)

@admin_bp.route('/admin/users')
@login_required
def manage_users():
    admin_required()
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/user/<int:user_id>/ban', methods=['POST'])
@login_required
def ban_user(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash("You cannot ban yourself!", "danger")
        return redirect(url_for('admin.manage_users'))
    user.is_banned = True
    db.session.commit()
    flash(f"User {user.username} has been banned.", "success")
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/user/<int:user_id>/unban', methods=['POST'])
@login_required
def unban_user(user_id):
    admin_required()
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()
    flash(f"User {user.username} has been unbanned.", "success")
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/reports')
@login_required
def manage_reports():
    admin_required()
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    return render_template('admin/reports.html', reports=reports)

@admin_bp.route('/admin/report/<int:report_id>/resolve', methods=['POST'])
@login_required
def resolve_report(report_id):
    admin_required()
    report = Report.query.get_or_404(report_id)
    report.resolved = True
    db.session.commit()
    flash("Report marked as resolved.", "success")
    return redirect(url_for('admin.manage_reports'))
