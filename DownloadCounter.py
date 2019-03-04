from builtins import Exception, repr, len


class Entry:
    def __init__(self, key, value, id=None):
        self.key = key
        self.value = value
        self.id=id

class DownloadCounter:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur

    def Increment(self, filename):
        try:
            entry = self.readEntry(filename)
            if entry:
                print('Download count of ' + filename + ' old value ' + str(entry.value))
                entry.value = int(entry.value) + 1
                print('Download count of ' + filename + ' new value ' + str(entry.value))
                self.writeEntry(entry)
            else:
                entry = Entry(filename, 1)
                print('Download count of ' + filename + ' new value' + str(entry.value))
                self.writeEntry(entry)
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def writeEntry(self, Entry):
        try:
            query = '''SELECT * FROM downloads WHERE key = ?'''
            self.cur.execute(query, (Entry.key,))
            data=self.cur.fetchall()
            if len(data) > 0:
                self.updateEntry(Entry)
            else:
                self.insertEntry(Entry)
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def insertEntry(self, Entry):
        try:
            query = '''INSERT INTO downloads(key, value) VALUES(?,?)'''
            self.cur.execute(query, (Entry.key, Entry.value))
            self.conn.commit()
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def readEntry(self, key):
        try:
            self.cur.execute("select * from downloads where key=?", (key,))
            self.conn.commit()
            lt = self.cur.fetchone()
            entry = Entry(lt[1], lt[2], lt[0])
            return entry
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def getEntry(self, id):
        try:
            self.cur.execute("select * from downloads where id=?", (id,))
            self.conn.commit()
            lt = self.cur.fetchone()
            setting = Entry(lt[1], lt[2], lt[0])
            return setting
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def updateEntry(self, Entry):
        try:
            query = '''UPDATE downloads SET value=? where key=?'''
            self.cur.execute(query, (Entry.value, Entry.key))
            self.conn.commit()
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return None

    def deleteEntry(self, key):
        try:
            query = '''DELETE FROM downloads WHERE key=?'''
            self.cur.execute(query,(key,))
            self.conn.commit()
            return None
        except Exception as ex:
            print('exception' + repr(ex))
            return repr(ex)

    def getEntries(self):
        try:
            query = '''SELECT key, value, id FROM downloads'''
            self.cur.execute(query)
            lts = self.cur.fetchall()
            entries = [Entry(lt[0], lt[1], lt[2]) for lt in lts]
            return entries, None
        except Exception as ex:
            return [], repr(ex)