import sqlite3

class db_obj:

    def __init__(self):
        self.__conn = None
        self.__cursor = None

    def create_db(self,name):
        try:
            self.__conn = sqlite3.connect(name)
            return "Database is set or created."
        except Exception as e:
            print (e)

    
    def set_cursor(self):
        try:
            if(self.__cursor is None):
                self.__cursor = self.__conn.cursor()
                return "cursor is set."
            else:
                pass
        except Exception as e:
            print (e)

    def create_table(self,table_name,**col_daty):
        if(len(col_daty) == 0):
            return "Invalid Args."
        else:
            try:
                statement_string = "CREATE TABLE "+str(table_name)+" ("
                for col in col_daty:
                    statement_string += col +" "+col_daty[col]+","
                statement_string = statement_string[:-1:] + ")"
                self.__cursor.execute(statement_string)
                return "Successfully Created."
            except Exception as e:
                print (e)
    
    def close_db(self):
        self.__conn.close()
        self.__cursor = None
        self.__conn = None

    
        
