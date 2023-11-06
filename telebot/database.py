import sqlite3


def connect(func):
    def wrapper():
        con = sqlite3.connect('mentorsDatabase.db')
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS mentors(name TEXT,
                                                          tgId TEXT,
                                                          month TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS candidate(name TEXT,
                                                            tgId TEXT,
                                                            month TEXT)""")
        func(cur)
        con.commit()
        con.close()
    return wrapper()


def insertMenInfo(name, tgId, month):
    checkDouble = getMentor(name)
    if (checkDouble != name) or checkDouble is None:
        @connect
        def insertMenInfoDB(cur=None):
            cur.execute("""INSERT INTO mentors VALUES(?, ?, ?)""", (name, tgId, month))
        insertMenInfoDB


def deleteMenInfo(name):
    @connect
    def deleteMenInfoDB(cur=None):
        cur.execute(f"""DELETE FROM mentors WHERE name = '{name}'""")
    deleteMenInfoDB


def updateMenInfo(name):
    @connect
    def updateMenInfoDB(cur=None):
        cur.execute(f"""SELECT month FROM mentors WHERE name = '{name}'""")
        rec = cur.fetchall()
        month = 0
        for el in rec:
            month = el[0]
        if int(month) <= 6:
            cur.execute(f"""UPDATE mentors SET month = month + 1 WHERE name = '{name}'""")
    updateMenInfoDB


def getMenInfo():
    values = []

    @connect
    def getMenInfoDB(cur=None):
        cur.execute("""SELECT * FROM mentors""")
        record = cur.fetchall()

        for el in record:
            values.append([el[0], el[1], el[2]])

    return values


def getMentor(tgid):
    mentors = getMenInfo()
    for el in mentors:
        if tgid == el[1]:
            return el[1]
    return None


def getFullMentorInfo(tgid):
    mentors = getMenInfo()
    for el in mentors:
        if tgid == el[1]:
            return el
    return None


def getMenMonth(tgid):
    value = []

    @connect
    def getMenMonthDB(cur=None):
        cur.execute(f"""SELECT month FROM mentors WHERE tgId = '{tgid}'""")
        rec = cur.fetchall()
        for el in rec:
            value.append(el[0])

    getMenMonthDB
    return value[0]


def insertCanInfo(name, tgId, month):
    checkDouble = getMentor(name)
    if (checkDouble != name) or checkDouble is None:
        @connect
        def insertCanInfoDB(cur=None):
            cur.execute("""INSERT INTO candidate VALUES(?, ?, ?)""", (name, tgId, month))
        insertCanInfoDB


def deleteCanInfo(name):
    @connect
    def deleteCanInfoDB(cur=None):
        cur.execute(f"""DELETE FROM candidate WHERE name = '{name}'""")
    deleteCanInfoDB


def getCanInfo():
    values = []

    @connect
    def getCanInfoDB(cur=None):
        cur.execute("""SELECT * FROM candidate""")
        record = cur.fetchall()
        for el in record:
            values.append([el[0], el[1], el[2]])

    return values


def getCandidate(name):
    candidates = getCanInfo()
    for el in candidates:
        if name == el[0]:
            return el
    return None
