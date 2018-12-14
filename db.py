import sqlite3
import os

class SQL_DB:
    def __init__( self , files, db_file = "prob.db"):
        self.db_file = db_file
        self.files = files
        self.cache = dict()
        if os.path.exists(db_file):
            os.remove(db_file)
        self.init_db()

    def init_db(self):
        conn = self.get_db_conn()
        for file_name in self.files:
            with open(file_name) as f:
                data = [line.rstrip() for line in f]
            table_name = data[0]
            rows = data[1:]
            data_row = [ row.split(',') for row in rows ]
            num_cols = len(data_row[0]) - 1
            self.createTable(conn, table_name, num_cols)
            self.batch_insert(conn, table_name, data_row, num_cols)
        conn.commit()

    def get_db_conn(self):
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except:
            print('Database error')
        return None

    def createTable(self, conn, tableName, numColumns):
        rows = ""
        for i in range(numColumns):
            column_name = "col" + str(i)
            rows += column_name + " integer,"
        rows += "prob real"
        sql = 'CREATE TABLE {} ({})'.format(tableName, rows)
        conn.execute(sql)

    def batch_insert(self, conn, tableName, data, numColumns):
        values = ''
        for i in range(numColumns):
            values += '?,'
        values += '?'
        insert_data = [tuple(row) for row in data]
        conn.executemany('INSERT INTO {} VALUES ({})'.format(tableName, values), insert_data)

    def get_prob(self, tableName, column_values):
        key = ''
        for val in column_values:
            key += str(val) + '/'
        key += tableName
        if  key in self.cache:
            return self.cache[key]
        conn = self.get_db_conn()
        column_name = ""
        for i in range(len(column_values)):
            if i == 0:
                column_name += "col" + str(i) + " = " + str(column_values[i]) + " "
            else:
                column_name += "AND " + "col" + str(i) + " = " + str(column_values[i])

        sql = 'SELECT prob FROM {} WHERE {}'.format(tableName, column_name)
        # print(sql)
        try:
            for row in conn.execute(sql):
                conn.close()
                # print(float(row[0]))
                res = float(row[0])
                self.cache[key] = res
                return res 
        except:
            print("error!")
            return 1

        return 0