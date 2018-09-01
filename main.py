import dbhelper
import time
import os
from log import *
from flask import Flask, render_template, request, send_from_directory, json, session, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from Settings import Settings, Setting
import config
from FileView import FileView

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + APP_ROOT + '/login.db'
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))


@app.route("/")
def index():
    registeradmin()
    target = os.path.join(APP_ROOT, 'files/')
    if not os.path.isdir(target):
        os.mkdir(target)
    return render_template("welcome.html")



@app.route('/files/<path:filename>', methods=['GET'])
def download(filename):
    target = os.path.join(APP_ROOT, 'files/')
    return send_from_directory(directory=target, filename=filename)


@app.route('/files', methods=['POST', 'GET', 'DELETE', 'PATCH'])
@login_required
def list_files():
    if request.method == 'GET':
        """Endpoint to list files on the server."""
        target = os.path.join(APP_ROOT, 'files/')
        files = []
        for filename in os.listdir(target):
            path = os.path.join(target, filename)
            if os.path.isfile(path):
                fileview = FileView(path)
                files.append(fileview)
        return render_template('files.html', files=files)

    elif request.method == 'DELETE':
        """Delete file"""
        target = os.path.join(APP_ROOT, 'files/')
        filename = request.form['filename']
        filepath = os.path.join(target, filename)
        print('filepath=' + str(filepath))
        try:
            os.remove(filepath)
            print('File deleted : ' + filename)
            return "success"
        except Exception as ex:
            print('File Delete Error: ' + repr(ex))
            return "failed"

    elif request.method == 'POST':
        """Upload file"""
        target = os.path.join(APP_ROOT, 'files/')
        if not os.path.isdir(target):
            os.mkdir(target)
        file = request.files.getlist("file")[0]
        filename = file.filename
        destination = "/".join([target, filename])
        try:
            file.save(destination)
            print('File saved : ' + file.filename)
            return "success"
        except Exception as ex:
            print('File Save Error: ' + repr(ex))
            return "failed"

    elif request.method == 'PATCH':
        """Rename file"""
        target = os.path.join(APP_ROOT, 'files/')
        oldname = request.form['oldname']
        newname = request.form['newname']
        oldpath = os.path.join(target, oldname)
        print('oldpath=' + str(oldpath))
        newpath = os.path.join(target, newname)
        print('newpath=' + str(newpath))
        try:
            os.rename(oldpath, newpath)
            print('File renamed; Old name : ' + oldname + " => New name :" + newname)
            return "success"
        except Exception as ex:
            print('File Rename Error: ' + repr(ex))
            return "failed"


@app.route('/files/rename', methods=['POST'])
@login_required
def rename():
    target = os.path.join(APP_ROOT, 'uploads/')
    oldname = request.form['oldname']
    newname = request.form['newname']
    oldpath = os.path.join(target, oldname)
    print('oldpath=' + str(oldpath))
    newpath = os.path.join(target, newname)
    print('newpath=' + str(newpath))
    os.rename(oldpath, newpath)
    return "success"


@app.route('/files/delete', methods=['POST'])
@login_required
def delete_file():
    target = os.path.join(APP_ROOT, 'uploads/')
    filename = request.form['filename']
    filepath = os.path.join(target, filename)
    print('filepath=' + str(filepath))
    os.remove(filepath)
    return "success"


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                session['user'] = user.username
                return render_template("welcome.html", user=username)
            else:
                return render_template("login.html", message="Password is incorrect")
        else:
            return render_template("login.html", message="User is not exists")
    elif request.method == 'GET':
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return render_template("welcome.html")


def registeradmin():
    if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI']):
        db.create_all()
        print("db created : " + app.config['SQLALCHEMY_DATABASE_URI'])
        user = User.query.filter_by(username=config.USER_NAME).first()
        if not user:
            hashed_password = generate_password_hash(config.PASSWORD, method='sha256')
            admin = User(username=config.USER_NAME, password=hashed_password)
            db.session.add(admin)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/logs')
@login_required
def logs_home():
    conn, cur = dbhelper.getDb()
    logdb = LogDb(conn, cur)
    logs, err = logdb.getLogs()
    if err == None:
        return render_template('logs.html', logs=logs)
    else:
        return render_template('error.html', exception=err)


@app.route('/log/<int:log_id>', methods=['GET'])
def api_log_from_id(log_id):
    conn, cur = dbhelper.getDb()
    logdb = LogDb(conn, cur)
    log, err = logdb.getLog(log_id)
    if log:
        print('Log returned :' + repr(log))
        return log.toJson()
    else:
        print('Error in getting log!')
        return err


@app.route('/log/all')
def api_log_all():
    conn, cur = dbhelper.getDb()
    logdb = LogDb(conn, cur)
    logs, err = logdb.getLogs()
    logsdicts = [x.toDict() for x in logs]
    return json.dumps(logsdicts)


@app.route('/log', methods=['POST', 'DEL'])
def api_log():
    if request.method == 'POST':
        try:
            conn, cur = dbhelper.getDb()
            username = request.form['username']
            appname = request.form['appname']
            version = request.form['version']
            type = request.form['type']
            createdate = request.form['createdate']
            content = request.form['content']
            senddate = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())
            logdb = LogDb(conn, cur)
            log = Log(username, appname, version, type, createdate, senddate, content)
            err = logdb.addLog(log)
            print('username = ' + username)
            print('appname = ' + appname)
            print('version = ' + version)
            print('type = ' + type)
            print('createdate = ' + createdate)
            print('content = ' + content)
            print('senddate = ' + senddate)
            return str(err)
        except Exception as ex:
            print(ex)
            return repr(ex)
    elif request.method == 'DEL':
        print('Delete entry')
        print(request.form)
        # concat json var with '[]' for calling array getted with request
        idlist = request.form.getlist('ids[]')
        print('IDS: ', idlist)
        if idlist == []:
            try:
                idlist = [request.form['id']]
                print('IDS: ', idlist)
            except:
                return json.dumps({'status': 'OK', 'idlist': idlist})

        print('IDS: ', idlist)
        print(json.dumps({'status': 'OK', 'idlist': idlist}))
        conn, cur = dbhelper.getDb()
        logdb = LogDb(conn, cur)
        for _id in idlist:
            print(_id)
            err = logdb.deleteLog(_id)
            print(err)
        return json.dumps({'status': 'OK', 'idlist': idlist})

@app.route('/content/<int:log_id>', methods=['GET'])
def api_content(log_id):
    print('Get entry content')
    print(log_id)
    conn, cur = dbhelper.getDb()
    logdb = LogDb(conn, cur)
    log, err = logdb.getLog(log_id)
    if log:
        print(log.content)
        return log.content
    else:
        return err


@app.route('/users')
@login_required
def users_home():
    conn, cur = dbhelper.getDb()
    logdb = LogDb(conn, cur)
    logs, err = logdb.getUserLogs()
    if err == None:
        return render_template('users.html', logs=logs)
    else:
        return render_template('error.html', err=err)

@app.route('/user/<int:id>', methods=['GET'])
def user_from_id(id):
    conn, cur = dbhelper.getDb()
    logdb = LogDb(conn, cur)
    log, err = logdb.getUserLog(id)
    if log:
        print('Log returned :' + repr(log._id))
        return log.toJson()
    else:
        print('Error in getting log!')
        return err


@app.route('/user', methods=['POST', 'DEL'])
def api_user():
    conn, cur = dbhelper.getUserDb()
    logdb = LogDb(conn, cur)
    if request.method == 'POST':
        try:
            username = request.form['username']
            appname = request.form['appname']
            version = request.form['version']
            createdate = request.form['createdate']
            userid = request.form['userid']
            senddate = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())

            log = UserLog(username, appname, version, createdate, senddate, userid)
            err = logdb.addUserLog(log)
            print('username = ' + username)
            print('appname = ' + appname)
            print('version = ' + version)
            print('createdate = ' + createdate)
            print('userid = ' + userid)
            print('senddate = ' + senddate)
            return str(err)
        except Exception as ex:
            print(ex)
            return repr(ex)
    elif request.method == 'DEL':
        id = request.form['id']
        try:
            logdb.deleteUserLog(id)
            print('User log deleted : id=' + repr(id))
        except Exception as ex:
            print('User log couldnr be deleted : id=' + id)
            print(ex)
            return repr(ex)


@app.route('/lognormal')
def api_log_normal():
    return "hello world"


@app.route('/newversion', methods=['GET'])
def new_version():
    conn, cur = dbhelper.getDb()
    settingdb = Settings(conn, cur)
    versionsetting = settingdb.readSetting(config.NEW_VERSION_KEY)
    return versionsetting.value


@app.route('/newversionurl', methods=['GET'])
def new_version_url():
    conn, cur = dbhelper.getDb()
    settingdb = Settings(conn, cur)
    versionsetting = settingdb.readSetting(config.NEW_VERSION_URL_KEY)
    return versionsetting.value


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn, cur = dbhelper.getDb()
    settingdb = Settings(conn, cur)
    if request.method == 'GET':
        listsettings, err = settingdb.getSettings()
        if err == None:
            return render_template('settings.html', settings=listsettings)
        else:
            return render_template('error.html', exception=err)
    elif request.method == 'POST':
        key = request.form['key']
        value = request.form['value']
        setting = Setting(key, value)
        settingdb.writeSetting(setting)
        listsettings, err = settingdb.getSettings()
        if err == None:
            return render_template('settings.html', settings=listsettings)
        else:
            return render_template('error.html', exception=err)


@app.route('/setting/<int:id>', methods=['GET'])
@login_required
def setting(id):
    conn, cur = dbhelper.getDb()
    settingdb = Settings(conn, cur)
    setting = settingdb.getSetting(id)
    print('key=' + str(setting.key))
    print('value=' + str(setting.value))
    print('id=' + str(setting.id))
    settingdict = {'key': setting.key, 'value': setting.value, 'id': setting.id}
    return json.dumps(settingdict)


@app.route('/setting/delete', methods=['POST'])
@login_required
def delete_setting():
    key = request.form['key']
    conn, cur = dbhelper.getDb()
    settingdb = Settings(conn, cur)
    settingdb.deleteSetting(key)
    listsettings, err = settingdb.getSettings()
    if err == None:
        return render_template('settings.html', settings=listsettings)
    else:
        return render_template('error.html', exception=err)


@app.route('/example')
def example():
    return render_template('example.html')

@app.route('/reset')
@login_required
def reset():
    try:
        dbhelper.resetDb()
        dbhelper.resetUserDb()
        dbhelper.resetSettingsDb()
        conn, cur = dbhelper.getDb()
        logdb = LogDb(conn, cur)
        log, err = logdb.getLog(1)

        if err == None:
            return log.name
        return "Database reset"
    except Exception as ex:
        return "Database Error: " + repr(ex)

if __name__ == "__main__":
    app.run(port=80, debug=True)
