from builtins import Exception, repr, len


class Setting:
    def __init__(self, key, value, id=None):
        self.key = key
        self.value = value
        self.id=id

class Settings:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

    def writeSetting(self, Setting):
        try:
            query = '''SELECT * FROM settings WHERE key = ?'''
            self.cur.execute(query, (Setting.key,))
            data=self.cur.fetchall()
            if len(data) > 0:
                self.updateSetting(Setting)
            else:
                self.insertSetting(Setting)
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def insertSetting(self, Setting):
        try:
            query = '''INSERT INTO settings(key, value) VALUES(?,?)'''
            self.cur.execute(query, (Setting.key, Setting.value))
            self.conn.commit()
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def readSetting(self, key):
        try:
            self.cur.execute("select * from settings where key=?", (key,))
            self.conn.commit()
            lt = self.cur.fetchone()
            setting = Setting(lt[1], lt[2], lt[0])
            return setting
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def getSetting(self, id):
        try:
            self.cur.execute("select * from settings where id=?", (id,))
            self.conn.commit()
            lt = self.cur.fetchone()
            setting = Setting(lt[1], lt[2], lt[0])
            return setting
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def updateSetting(self, Setting):
        try:
            query = '''UPDATE settings SET value=? where key=?'''
            self.cur.execute(query, (Setting.value, Setting.key))
            self.conn.commit()
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def deleteSetting(self, key):
        try:
            query = '''DELETE FROM settings WHERE key=?'''
            self.cur.execute(query,(key,))
            self.conn.commit()
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return repr(ex)


    def getSettings(self):
        try:
            query = '''SELECT key, value, id FROM settings'''
            self.cur.execute(query)
            lts = self.cur.fetchall()
            settings = [Setting(lt[0], lt[1], lt[2]) for lt in lts]
            return settings, None
        except Exception as ex:
            return [], repr(ex)


