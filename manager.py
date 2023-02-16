from __init_app__ import app
from models import db, User, TheftFir, Actions
from auth import bycrpyt, login_manager, LoginForm, RegisterForm
from config import config

from flask import render_template, redirect, url_for, request, abort, flash
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import desc
from functools import wraps
import datetime as dt
import pytz

IST = pytz.timezone('Asia/Kolkata')
# print(dt.datetime.now(IST).strftime('%Y-%m-%d %H:%M'))

def permission_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.get_role() != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required('ADMIN')(f)

#------------------------------  ROUTES ----------------------------------------------------

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/reported-crimes',methods=['GET'])
@login_required
def crimes_reported():
    print(current_user.username)

    firs=db.session.query(User).filter(User.id == current_user.id).first().tfirs
    print(firs)
    actions_list=[]
    for fir in firs:
        action_taken=db.session.query(Actions).filter(Actions.id==fir.id).first()
        if action_taken==None:
            actions_list.append(1)
        else:
            if action_taken.accepted==True:
                actions_list.append(2)
            else:
                actions_list.append(3)
    print(actions_list)
    return render_template('reported_crimes.html', firs=firs, action_list=actions_list)

@app.route('/reported-crimes/<int:id>', methods=['GET'])
@login_required
def crimes_details(id):
    fir=db.session.query(TheftFir).filter(TheftFir.id==id and TheftFir.username==current_user.username).first()
    if fir is None:
        return render_template('error.html')
    action_taken=db.session.query(Actions).filter(Actions.id==id).first()
    remarks=''
    actions=[]
    actions_timestamp=[]
    if action_taken is None:
        pass
    else:
        if action_taken.accepted==True:
            actions.append('Accepted, on investigation')
            actions_timestamp.append(action_taken.accepted_timeStamp)
        else:
            remarks=action_taken.remarks
            if remarks==None:
                remarks='No remarks'
            actions.append('Rejected')
            actions_timestamp.append(action_taken.rejected_timeStamp)
        if fir.closed==1:
            actions.append('Case closed')
            actions_timestamp.append(action_taken.closed_timeStamp)
    return render_template('crime_details.html', fir=fir, actions=actions, actions_timestamp=actions_timestamp,remarks=remarks)

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template("profile.html")

@app.route('/report-theft', methods=['GET','POST'])
@login_required
def report_theft():
    if request.method == 'GET':
        return render_template('report_theft.html')
    elif request.method == 'POST':
        req=request.form
        cname=req['cname']
        pname=req['pname']
        addr=req['address']
        mob=req['mob']
        email=req['email']
        place=req['place']
        date=req['date']
        time=req['time']
        aname=req['aname']
        desc=req['description']
        
        if time==None:
            time="not specified"

        print(cname, pname, addr, mob, email, place, date, time, aname, desc)

        try:
            ftime=dt.datetime.now(IST)
            # print(ftime)
            fir=TheftFir(id=None,ftime=ftime,username=current_user.username,cname=cname,pname=pname,address=addr,mob=mob,email=email,place=place,datetime=date+" "+time,aname=aname,description=desc,closed=0)
            db.session.add(fir)
            db.session.flush()
        except:
            db.session.rollback()
            return render_template('error.html')
        else:
            db.session.commit()
        # flash(f'FIR Successfully Submitted')
        return redirect('/reported-crimes')

#----------------------  POLICE ROUTES -------------------------------

@app.route('/police', methods=['GET'])
@login_required
@admin_required
def police_home():
    firs=db.session.query(TheftFir).order_by(desc(TheftFir.ftime)).all()
    closed=[]
    ongoing=[]
    new=[]
    for fir in firs:
        if fir.closed==1:
            closed.append(fir)
        else:
            actions=db.session.query(Actions).filter(Actions.id==fir.id).first()
            if actions is None:
                new.append(fir)
            else:
                ongoing.append(fir)
            
    return render_template('police_home.html', closed=closed, ongoing=ongoing, new=new)



@app.route('/police/action-page/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def action_page(id):
    if request.method=='GET':
        fir=db.session.query(TheftFir).filter(TheftFir.id==id).first()
        action_taken=db.session.query(Actions).filter(Actions.id==id).first()
        remarks=''
        actions=[]
        actions_timestamp=[]
        if action_taken is None:
            pass
        else:
            if action_taken.accepted==True:
                actions.append('Accepted')
                actions_timestamp.append(action_taken.accepted_timeStamp)
            else:
                remarks=action_taken.remarks
                if remarks==None:
                    remarks='No remarks'
                actions.append('Rejected')
                actions_timestamp.append(action_taken.rejected_timeStamp)
            if fir.closed==1:
                actions.append('Case closed')
                actions_timestamp.append(action_taken.closed_timeStamp)
        return render_template('action_page.html', fir=fir, actions=actions,actions_timestamp=actions_timestamp, remarks=remarks)
    elif request.method=='POST':
        try:
            action_id=request.form['action']
        except:
            return redirect('/police')
        print(action_id)
        action_taken=db.session.query(Actions).filter(Actions.id==id).first()
        action_timestamp=dt.datetime.now(IST)
        if action_id == 'A':
            if action_taken is None:
                action_taken=Actions(id=id,accepted=True,accepted_timeStamp=action_timestamp,rejected=False,remarks="")
                try:
                    db.session.add(action_taken)
                except:
                    db.session.rollback()
                else:
                    db.session.commit()
        elif action_id == 'R':
            remarks=request.form['remarks']
            print(remarks)
            if action_taken is None:
                action_taken=Actions(id=id,accepted=False,rejected=True,rejected_timeStamp=action_timestamp,remarks=remarks)
                try:
                    db.session.add(action_taken)
                except:
                    db.session.rollback()
                else:
                    db.session.commit()
                    fir=db.session.query(TheftFir).filter(TheftFir.id==id).first()
                    fir.closed=1
                    db.session.add(fir)
                    db.session.commit()
        else:
            fir=db.session.query(TheftFir).filter(TheftFir.id==id).first()
            fir.closed=1
            action=Actions.query.filter_by(id=id).first()
            action.closed_timeStamp=action_timestamp
            db.session.add(fir)
            db.session.add(action)
            db.session.commit()
        return redirect('/police')

@app.route('/police/profile', methods=['GET'])
@login_required
@admin_required
def police_profile():
    return render_template('police_profile.html')

#----------------------AUTH ROUTES-------------------------------
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        print(request.args)
        if 'next' in request.args:
            print(request.args['next'], 'next')
            return redirect(request.args['next'])
        else:
            return redirect(url_for("index"))
    return render_template('login.html',form=form)

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bycrpyt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data,password=hashed_password,role='USER')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html',form=form)

def create_police(username, passwd):
    user_exists = User.query.filter_by(username=username).first()
    if user_exists:
        pass
    else:
        hashed_password = bycrpyt.generate_password_hash(passwd)
        police_user=User(username=username, password=hashed_password, role='ADMIN')
        db.session.add(police_user)
        db.session.commit()

if __name__=="__main__":
    create_police(config['ADMIN_USERNAME'], config['ADMIN_PASSWORD'])
    app.run(debug=True)

