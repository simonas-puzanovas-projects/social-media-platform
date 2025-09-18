from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from .. import db

bp_auth = Blueprint("bp_auth", __name__, template_folder = "../templates")

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('bp_index.index'))
        else:
            flash('Invalid username or password!', 'error')
    
    if 'user_id' in session:
        return redirect(url_for("bp_index.index"))

    return render_template('login.html')

@bp_auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('login.html')
        
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('bp_auth.login'))
    
    return render_template('login.html')

@bp_auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bp_auth.login'))