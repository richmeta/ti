# coding: utf-8
import sqlite3
import os


class Store(object):
    store_file = '~/.ti-sheet.sqlite'
    conn = None
    fields = [
        'id', 'start', 'end', 'start_date', 'in_seconds', 'is_current', 'project', 'task']

    def __init__(self):
        store_path = os.path.expanduser(self.store_file)
        self.conn = sqlite3.connect(store_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row

        with self.conn:
            res = self.conn.execute('PRAGMA TABLE_INFO(tracking)')
            names = [tup[1] for tup in res.fetchall()]
            if not all(x in self.fields for x in names):
                self.create_schema()

    def create_schema(self):
        c = self.conn.cursor()
        ddl = """
            create table tracking (
              id integer PRIMARY KEY ,
              start text,
              end text,
              start_date text,
              in_seconds integer,
              is_current integer,
              project text,
              task text
            );
        """
        try:
            c.execute(ddl)
        except sqlite3.OperationalError:
            pass

    def get_current(self):
        c = self.conn.cursor()
        c.execute("select * from tracking where is_current = 1 order by start desc;")
        row = c.fetchone()
        if row:
            return row
        else:
            return None

    def add_tracking(self, task, project, start):
        with self.conn:
            self.conn.execute("insert into tracking (start, start_date, is_current, project, task)"
                              " values (?, ?, ?, ?, ?)", (str(start), str(start.to_date_string()), True, project, task))

    def finish_tracking(self, current, end):
        with self.conn:
            self.conn.execute("update tracking set is_current = ?, end = ?, in_seconds = ? where id = ?",
                              (False, str(end), (end-current['start']).total_seconds(), current['id']))

    def get_logs(self, gte, lte):
        with self.conn:
            c = self.conn.execute("select * from tracking where start_date >= ? and start_date <= ? order by start",
                                  (str(gte), str(lte)))
            return c.fetchall()

    def get_aggregated_logs(self, gte, lte):
        with self.conn:
            c = self.conn.execute("select project, task, sum(in_seconds) as total_seconds from tracking "
                                  "where start_date >= ? and start_date <= ? group by project, task",
                                  (str(gte), str(lte)))
            return c.fetchall()
