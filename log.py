import json

class Log:
    def __init__(self, username, appname, version, type, createdate, senddate, content, _id=None):
        self.username = username
        self.appname = appname
        self.version = version
        self.type = type
        self.createdate = createdate
        self.senddate = senddate
        self.content = content
        self._id = _id

    def toJson(self):
        logdict = {'username':self.username, 'appname':self.appname, 'version':self.version, 'type':self.type, 'createdate':self.createdate, 'senddate':self.senddate, 'content':self.content, 'id':self._id}
        return json.dumps(logdict)

    def toDict(self):
        logdict = {'username':self.username, 'appname':self.appname, 'version':self.version, 'type':self.type, 'createdate':self.createdate, 'senddate':self.senddate, 'content':self.content, 'id':self._id}
        return logdict

class UserLog:
    def __init__(self, username, appname, version, createdate, senddate, userid, _id=None):
        self.username = username
        self.appname = appname
        self.version = version
        self.createdate = createdate
        self.senddate = senddate
        self.userid = userid
        self._id = _id

    def toJson(self):
        logdict = {'username':self.username, 'appname':self.appname, 'version':self.version, 'createdate':self.createdate, 'senddate':self.senddate, 'userid':self.userid, 'id':self._id}
        return json.dumps(logdict)

class LogDb:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

    def addLog(self, log):
        try:
            query = '''INSERT INTO logs(username, appname, version, type, createdate, senddate, content) VALUES(?,?,?,?,?,?,?)'''
            self.cur.execute(query, (log.username, log.appname, log.version, log.type, log.createdate, log.senddate, log.content))
            self.conn.commit()
            return None
        except Exception as ex:
            return repr(ex)

    def addUserLog(self, userlog):
        try:
            query = '''INSERT INTO users(username, appname, version, createdate, senddate, userid) VALUES(?,?,?,?,?,?)'''
            self.cur.execute(query, (userlog.username, userlog.appname, userlog.version, userlog.createdate, userlog.senddate, userlog.userid))
            self.conn.commit()
            return None
        except Exception as ex:
            return repr(ex)

    def getLog(self, _id):
        try:
            query = '''SELECT username, appname, version, type, createdate, senddate, content, id FROM logs WHERE id=?'''
            self.cur.execute(query, (_id,))
            lt = self.cur.fetchone()
            log = Log(lt[0], lt[1], lt[2], lt[3], lt[4], lt[5], lt[6], lt[7])
            return log, None
        except Exception as ex:
            return None, repr(ex)

    def getUserLog(self, _id):
        try:
            query = '''SELECT username, appname, version, createdate, senddate, userid, id FROM users WHERE id=?'''
            self.cur.execute(query, (_id,))
            lt = self.cur.fetchone()
            log = UserLog(lt[0], lt[1], lt[2], lt[3], lt[4], lt[5], lt[6])
            return log, None
        except Exception as ex:
            return None, repr(ex)

    def getLogs(self):
        try:
            query = '''SELECT username, appname, version, type, createdate, senddate, content, id FROM logs'''
            self.cur.execute(query)
            lts = self.cur.fetchall()
            logs = [Log(lt[0], lt[1], lt[2], lt[3], lt[4], lt[5], lt[6], lt[7]) for lt in lts]
            return logs, None
        except Exception as ex:
            return [], repr(ex)

    def getUserLogs(self):
        try:
            query = '''SELECT username, appname, version, createdate, senddate, userid, id FROM users'''
            self.cur.execute(query)
            lts = self.cur.fetchall()
            logs = [UserLog(lt[0], lt[1], lt[2], lt[3], lt[4], lt[5], lt[6]) for lt in lts]
            return logs, None
        except Exception as ex:
            return [], repr(ex)

    def deleteLog(self, _id):
        try:
            query = '''DELETE FROM logs WHERE id=?'''
            self.cur.execute(query, (_id,))
            self.conn.commit()
            return None
        except Exception as ex:
            return repr(ex)

    def deleteUserLog(self, _id):
        try:
            query = '''DELETE FROM users WHERE id=?'''
            self.cur.execute(query, (_id,))
            self.conn.commit()
            return None
        except Exception as ex:
            return repr(ex)

    def updateLog(self, log):
        try:
            query = '''UPDATE logs SET username=?, appname=?, type=?, version=?, createdate=?, senddate=?, content=?,WHERE id=?'''
            self.cur.execute(query, (log.username, log.appname, log.version, log.type, log.createdate, log.senddate, log.content, log._id))
            self.conn.commit()
            return None
        except Exception as ex:
            return repr(ex)
