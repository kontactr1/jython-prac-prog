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

    def read_schema(self):
        pass

    def custom_query(self,statement):
        try:
            self.self.__cursor.execute(statement_string)
            print ("Sucessfully Excecuted.")
        except Exception as e:
            print(e)

    def commit(self):
        try:
            self.__conn.commit()
        except Exception as e:
            print (e)

    @staticmethod
    def get_obj():
        try:
            return db_obj()
        except:
            print ("Problem occurred.")
            return None


    def insert_data(self,table_name,**col_data):
        if(len(col_data) == 0):
            return "Invalid Args."
        else:
            try:
                statement_string = "INSERT INTO "+str(table_name)+" ("
                statement_string1 = " VALUES("
                for col in col_data:
                    statement_string += col +","
                    if(type(col_data[col]) != type(1)):
                        statement_string1 += "'{0}'".format(col_data[col]) +","
                    else:
                        statement_string1 += str(col_data[col]) +","
                statement_string = statement_string[:-1:] + ")"
                statement_string1 = statement_string1[:-1:] + ")"
                print (statement_string+statement_string1)
                self.__cursor.execute(statement_string+statement_string1)
                return "Successfully Inserted."
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

    
        
