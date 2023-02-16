from flask import Flask, request, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import random
# random_id = ' '.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])

db=SQLAlchemy()
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///crime-reporting.sqlite3"
db.init_app(app)
app.app_context().push()

class TheftFir(db.Model):
    __tablename__='theft_fir'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String, db.ForeignKey('User.username'), primary_key=True)
    cname=db.Column(db.String, nullable=False)
    pname=db.Column(db.String, nullable=False)
    address=db.Column(db.String, nullable=False)
    mob=db.Column(db.String, nullable=False)
    email=db.Column(db.String, nullable=False)
    place=db.Column(db.String, nullable=False)
    date=db.Column(db.String, nullable=False)
    aname=db.Column(db.String, nullable=False)
    description=db.Column(db.String, nullable=False)
    closed=db.Column(db.Integer, nullable=False)

class Actions(db.Model):
    __tablename__='actions'
    id=db.Column(db.Integer, db.ForeignKey('theft_fir.id'), primary_key=True)
    accepted=db.Column(db.Boolean)
    rejected=db.Column(db.Boolean)
    remarks=db.Column(db.String)

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/reported-crimes',methods=['GET'])
def crimes_reported():
    firs=db.session.query(TheftFir).all()
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
def crimes_details(id):
    fir=db.session.query(TheftFir).filter(TheftFir.id==id).first()
    action_taken=db.session.query(Actions).filter(Actions.id==id).first()
    remarks=''
    if action_taken==None:
        action_taken='Pending'
    else:
        if action_taken.accepted==True:
            action_taken='On Investigation'
        else:
            remarks=action_taken.remarks
            if remarks==None:
                remarks='No remarks'
            action_taken='Rejected'
    return render_template('crime_details.html', fir=fir, action=action_taken, remarks=remarks)

@app.route('/profile', methods=['GET'])
def profile():
    return render_template("profile.html")

@app.route('/report-theft', methods=['GET','POST'])
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
            fir=TheftFir(id=None,cname=cname,pname=pname,address=addr,mob=mob,email=email,place=place,date=date+" "+time,aname=aname,description=desc,closed=0)
            db.session.add(fir)
            db.session.flush()
        except:
            db.session.rollback()
            return render_template('error.html')
        else:
            db.session.commit()
            # flash(f'FIR Successfully Submitted')
            return redirect('/reported-crimes')

#-----------------------------------------------------
@app.route('/police', methods=['GET'])
def police_home():
    firs=db.session.query(TheftFir).all()
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
def action_page(id):
    if request.method=='GET':
        fir=db.session.query(TheftFir).filter(TheftFir.id==id).first()
        action_taken=db.session.query(Actions).filter(Actions.id==id).first()
        op=''
        remarks=''
        if action_taken==None:
            op='Pending'
        else:
            if action_taken.accepted==True:
                op='On Investigation'
            else:
                remarks=action_taken.remarks
                if remarks==None:
                    remarks='No remarks'
                op='Rejected'
        return render_template('action_page.html', fir=fir, action=op, remarks=remarks)
    elif request.method=='POST':
        try:
            action_id=request.form['action']
        except:
            return redirect('/police')
        print(action_id)
        action_taken=db.session.query(Actions).filter(Actions.id==id).first()
        if action_id == 'A':
            if action_taken is None:
                action_taken=Actions(id=id,accepted=True,rejected=False,remarks="")
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
                action_taken=Actions(id=id,accepted=False,rejected=True,remarks=remarks)
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
            db.session.add(fir)
            db.session.commit()
        return redirect('/police')

@app.route('/police/profile', methods=['GET'])
def police_profile():
    return render_template('police_profile.html')

if __name__=='__main__':
    app.run(debug=True)

