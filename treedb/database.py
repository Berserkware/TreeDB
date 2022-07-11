import json

class AuthenticationError(Exception):
    pass

class ArgumentError(Exception):
    pass

class TreeClient:
    def __init__(self):
        self.Authenticated = False
        self.currentUsername = None
        self.currentPassword = None
        self.currentDB = None
        self.currentData = None

    def createDB(self, DBName: str, username: str, password: str):
        with open(f'{DBName}.tdb', 'wb') as db:
            db.write(f'DBName: {DBName}\nusername: {username}\npassword: {password}\n\r\n\r{"{}"}'.encode('UTF-8'))

    def openDB(self, DBName: str, username: str, password: str):
        with open(f'{DBName}.tdb', 'rb') as db:
            db = db.read()
            meta, data = db.split(b'\n\r\n\r')
            data = json.loads(data.decode('UTF-8'))
            rawHeaders = meta.decode('UTF-8').split('\n')
            headers = {}
            for header in rawHeaders:
                keyAndValue = header.split(': ')
                headers[keyAndValue[0]] = ': '.join(keyAndValue[1:])

        if username == headers['username'] and password == headers['password']:
            self.currentUsername = username
            self.currentPassword = password
            self.currentDB = DBName
            self.currentData = data
            self.Authenticated = True
        else:
            raise AuthenticationError

    def closeDB(self):
        self.currentUsername = None
        self.currentPassword = None
        self.currentDB = None
        self.currentData = None
        self.Authenticated = False

    def createCollumn(self, collumnName: str, placeholder=None):
        collumns = list(self.currentData.keys())
        if collumnName in collumns:
            raise ValueError('Collumn already exists!')
        
        if len(collumns) == 0:
            self.currentData[collumnName] = []
            self._saveDB()
            return
        else:
            if len(self.currentData[collumns[0]]) == 0:
                self.currentData[collumnName] = []
                self._saveDB()
                return

        if len(self.currentData[collumns[0]]) != 0:
            if placeholder is None:
                raise ValueError('You need to supply a placeholder if your database has and entries.')
            values = []
            for value in range(len(self.currentData[collumns[0]])):
                values.append(placeholder)

            self.currentData[collumnName] = values

        self._saveDB()

    def createEntry(self, **kwargs):
        newData = self.currentData.copy()
        collumns = list(self.currentData.keys())
        for collumn in collumns:
            try:
                value = kwargs[collumn]
                newData[collumn].append(value)
            except KeyError:
                raise KeyError(f'Value needed for collumn  \'{collumn}\'')
        
        self.currentData = newData
        self._saveDB()
            
    def _saveDB(self):
        with open(f'{self.currentDB}.tdb', 'wb') as db:
            db.write(f'DBName: {self.currentDB}\nusername: {self.currentUsername}\npassword: {self.currentPassword}\n\r\n\r{json.dumps(self.currentData)}'.encode('UTF-8'))

    def retrieve(self, collumn=None, value=None, collumnNeeded=None):
        if collumn not in list(self.currentData.keys()) and collumn is not None:
            raise ValueError(f'Could not find collumn \'{collumn}\'')
        elif collumnNeeded not in list(self.currentData.keys()) and collumnNeeded is not None:
            raise ValueError(f'Could not find collumn \'{collumnNeeded}\'')

        if collumn is None and value is not None or collumn is not None and value is None:
            raise ArgumentError('If the collumn argument is provided you need to supply a value argument, and vise versa.')

        if collumn is None:
            if collumnNeeded is None:
                return self.currentData
            else:
                return self.currentData[collumnNeeded]
        else:
            if collumnNeeded is None:
                foundValue = False
                lineData = {}
                for index, line in enumerate(self.currentData[collumn]):
                    if line == value:
                        for col in list(self.currentData.keys()):
                            lineData[col] = self.currentData[col][index]
                        foundValue = True
                        break

                if foundValue:
                    return lineData
                raise ValueError(f'Could not find \'{value}\' in collumn \'{collumn}\'')

            else:
                lineData = {}
                for index, line in enumerate(self.currentData[collumn]):
                    if line == value:
                        return self.currentData[collumnNeeded][index]
