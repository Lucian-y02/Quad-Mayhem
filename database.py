import sqlite3
import pickle

import pygame as pg

pg.init()


class DBase:
    _db = None

    def __init__(self, name=None):
        if name and not DBase._db:
            DBase._db = sqlite3.connect(name)

    @staticmethod
    def connect():
        return DBase._db.cursor()

    @staticmethod
    def commit():
        DBase._db.commit()


class Table:
    def __init__(self, name):
        self.name = name
        self.cur = DBase().connect()
        sql = f'''CREATE TABLE IF NOT EXISTS {self.name} (
              ID INTEGER,
              DATA BLOB (4096)
              );'''
        self.cur.execute(sql)

    def add(self, data):
        sql = f'''SELECT max(id) FROM {self.name}'''
        id = self.cur.execute(sql).fetchone()[0]
        if id:
            id += 1
        else:
            id = 1
        sql = f'''INSERT INTO {self.name} (id, data) VALUES (?, ?)'''
        self.cur.execute(sql, (id, pickle.dumps(data)))
        return id

    def get(self, id=None):
        if id:
            sql = f'''SELECT id, data FROM {self.name} WHERE id = {id}'''
        else:
            sql = f'''SELECT id, data FROM {self.name}'''
        res = self.cur.execute(sql)
        dic = {}
        for rec in res:
            dic[rec[0]] = pickle.loads(rec[1])
        return dic

    def put(self, id, data):
        sql = f'''SELECT data FROM {self.name} WHERE id = {id}'''
        if self.cur.execute(sql).fetchone():
            sql = f'UPDATE {self.name} set data = ? WHERE id = {id}'
            self.cur.execute(sql, (pickle.dumps(data), ))
        else:
            sql = f'INSERT INTO {self.name} (id, data) VALUES (?, ?)'
            self.cur.execute(sql, (id, pickle.dumps(data)))

    def put_image(self, id, value: pg.Surface):
        data = (pg.image.tostring(value, 'RGB'), value.get_size())
        self.put(id, data)

    def get_image(self, id):
        dic = self.get(id)
        for key, val in dic.items():
            value = pg.image.fromstring(val[0], val[1], 'RGB')
            dic[key] = value
        return dic


if __name__ == '__main__':
    DBase('images.db')
    screen = pg.display.set_mode((1000, 600))
    image1 = pg.image.load("data/teamchoiceffa.png")
    Table('images').put_image(28, image1)
    flag = True
    current = 26
    DBase('images.db').commit()
    while flag:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                flag = False
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_d or event.key == pg.K_RIGHT:
                    current += 1
                    print(current)
                if event.key == pg.K_a or event.key == pg.K_LEFT:
                    current -= 1
                    print(current)
        screen.fill('blue')
        image = Table('images').get_image(current)[current].convert()
        image.set_colorkey('white')
        screen.blit(image, (0, 0))
        pg.display.flip()
    pg.quit()
