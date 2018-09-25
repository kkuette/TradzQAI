from pymongo import MongoClient
from copy import deepcopy
import warnings
from threading import Thread
import time
import json

class dataBaseManager(object):

    def __init__(self, name=None, host='127.0.0.1', port=27017, clients=None):
        '''
        args:
            Clients : dict filled with name of client and MongoClient
                      dict(name = client)
        '''

        self.clients = dict()

        # Init default values
        self.last_client = None
        self.last_db = None
        self.last_collection = None
        self.runner = []

        if clients:
            for name, client in clients.items():
                self.addClient(client, name)
        elif name:
            self.addClient(MongoClient(host, port), name)

    def closeAllClients(self):
        for name, value in self.clients.items():
            print ('Client %s closed.' % name)
            self.getGivenClient(name).close()

    def closeClient(self, name):
        self.getGivenClient(name).close()

    def setFull(self, collection, db, name):
        self.setClient(name)
        self.setDB(db)
        self.setCollection(collection)

    def setClient(self, name):
        dbmErrorHandler.ClientNameError(name)
        self.last_client = name

    def setDB(self, db):
        dbmErrorHandler.DataBaseError(db)
        self.last_db = db

    def setCollection(self, collection):
        dbmErrorHandler.CollectionError(collection)
        self.last_collection = collection

    def addClient(self, client, name):
        '''
        Add a new client
            args:
                client : MongoClient object
                name : Name of client as str
        '''

        dbmErrorHandler.ClientNameError(name)
        dbmErrorHandler.ClientError(client)

        self.last_client = name
        new_client = dict(
            client = client,
            databases = dict()
        )
        self.clients[name] = new_client

    def addDB(self, db, name=None):
        '''
        Add a database to client
            args:
                db: Database name as str or list of str
                name: Client name as str, default last added client
        '''

        if not name:
            name = self.last_client

        dbmErrorHandler.ClientNameError(name)

        if isinstance(db, str):
            self.clients[name]['databases'][db] = dict()
            self.last_db = db
        elif isinstance(db, list):
            for item in db:
                dbmErrorHandler.DataBaseError(item)
                self.clients[name]['databases'][item] = dict()
                self.last_db = item
        else:
            dbmErrorHandler.DataBaseError(db)


    def addCollection(self, collection, db=None, name=None):
        '''
        Add a collection to the db from client
            args:
                collection: Collection name as str or list of str
                db: Database name as str, default last added database
                name: client name as str, default last added client
        '''

        if not db:
            db = self.last_db
        if not name:
            name = self.last_client

        dbmErrorHandler.DataBaseError(db)
        dbmErrorHandler.ClientNameError(name)

        if isinstance(collection, str):
            self.clients[name]['databases'][db][collection] = dict(
                id = -1,
                current_id = -1,
                data = []
            )
            self.last_collection = collection
        elif isinstance(collection, list):
            for item in collection:
                dbmErrorHandler.CollectionError(item)
                self.clients[name]['databases'][db][item] = dict(
                    id = -1,
                    current_id = -1,
                    data = []
                )
                self.last_collection = item
        else:
            dbmErrorHandler.CollectionError(collection)

    def addData(self, data, collection=None, db=None, name=None):
        '''
        Add data to collection in the db from client
            args:
                data: data as dict or list of dict
                collection: Collection name as str, default last added collection
                db: Database name as str, default last added database
                name: client name as str, default last added client
        '''

        if not name:
            name = self.last_client
        if not db:
            db = self.last_db
        if not collection:
            collection = self.last_collection

        dbmErrorHandler.CollectionError(collection)
        dbmErrorHandler.DataBaseError(db)
        dbmErrorHandler.ClientNameError(name)

        if self.clients[name]['databases'][db][collection]['id'] == -1:
            self.clients[name]['databases'][db][collection]['id'] = \
                self.getGivenCollection().count() - 1

        if isinstance(data, dict):
            self.clients[name]['databases'][db][collection]['id'] += 1
            data['id'] = self.clients[name]['databases'][db][collection]['id']
            self.clients[name]['databases'][db][collection]['data'].append(deepcopy(data))

        elif isinstance(data, list):
            for item in data:
                dbmErrorHandler.DataError(item)
                self.clients[name]['databases'][db][collection]['id'] += 1
                item['id'] = self.clients[name]['databases'][db][collection]['id']
                self.clients[name]['databases'][db][collection]['data'].append(deepcopy(item))
        else:
            dbmErrorHandler.DataError(data)

    def getClients(self):
        ''' Get all clients '''
        return self.clients

    def getCurrentClient(self):
        ''' Get current client dict '''
        return self.clients[self.last_client]

    def getCurrentDataBase(self):
        ''' Get current database dict '''
        return self.clients[self.last_client]['databases'][self.last_db]

    def getCurrentCollection(self):
        ''' Get current collection dict '''
        return self.clients[self.last_client]['databases'][self.last_db][self.last_collection]

    def getGivenClient(self, name=None):
        ''' Get Client() '''

        if not name:
            name = self.last_client
        dbmErrorHandler.ClientNameError(name)
        return self.clients[name]['client']

    def getGivenDB(self, db=None, name=None):
        ''' Get Client()[database] '''

        if not db:
            db = self.last_db
        dbmErrorHandler.DataBaseError(db)
        return self.getGivenClient(name)[db]

    def getGivenCollection(self, collection=None, db=None, name=None):
        ''' Get Client()[database][collection] '''

        if not collection:
            collection = self.last_collection
        dbmErrorHandler.CollectionError(collection)
        return self.getGivenDB(db, name)[collection]

    def getLastClient(self):
        return deepcopy(self.last_client)

    def getLastDB(self):
        return deepcopy(self.last_db)

    def getLastCollection(self):
        return deepcopy(self.last_collection)

    def getClientsNames(self):
        '''
        Get all clients name
            return:
                list of clients
        '''

        _clients = []
        for name, client in self.clients.items():
            _clients.append(name)
        return _clients

    def getDBs(self, name=None):
        '''
        Get all databases if no client name is specified,
        else return all databases from a given client name
            args:
                name: client name as str, default None
            return:
                dict(
                    clientname: list of databases
                )
        '''
        if name:
            name = self.last_name

        dbmErrorHandler.ClientNameError(name)

        _db = dict()
        if name:
            _db[name] = []
            for db, value in self.clients[name]['databases'].items():
                _db[name].append(db)
        else:
            for name, client in self.clients.items():
                _db[name] = []
                for db, value in self.clients[name]['databases'].items():
                    _db[name].append(db)
        return _db

    def getCollections(self, db=None, name=None):
        '''
        Get all collections in database in all clients if no client is specified,
        else if a database is specified, get all collections in a given database from all clients,
        else if a client name is specified get all collections in databases from a given client,
        else database and client name are specified get all collections in a given database from a given client.
            args:
                db: Database name as str, default None
                name: client name as str, default None
            return:
                dict(
                    clientname: dict(
                        database: list of collections
                    )
                )
        '''

        if not name:
            name = self.last_client
        if not db:
            db = self.last_db

        dbmErrorHandler.ClientNameError(name)
        dbmErrorHandler.DataBaseError(db)

        _collections = dict()
        if db and name:
            _collections[name] = dict()
            _collections[name][db] = []
            for collections, values in self.clients[name]['databases'][db].items():
                _collections.append(collections)
        elif db:
            for name, client in self.clients.items():
                _collections[name] = dict()
                for _db, value in self.clients[name]['databases'].items():
                    if _db == db:
                        _collections[name][_db] = []
                        for collections, values in self.clients[name]['databases'][_db].items():
                            _collections[name][_db].append(collections)
        elif name:
            _collections[name] = dict()
            for _db, value in self.clients[name]['databases'].items():
                _collections[name][_db] = []
                for collections, values in self.clients[name]['databases'][_db].items():
                    _collections[name][_db].append(collections)
        else:
            for name, client in self.clients.items():
                _collections[name] = dict()
                for _db, value in self.clients[name]['databases'].items():
                    _collections[name][_db] = []
                    for collections, values in self.clients[name]['databases'][_db].items():
                        _collections[name][_db].append(collections)
        return _collections

    def getCollectionData(self, collection=None, db=None, name=None):
        '''
        Get data from a given collection.
            args:
                collection: Collection name as str, default None
                db: Database name as str, default None
                name: Client name as str, default None
            return:
                list of dict
        '''
        if not name:
            name = self.last_client
        if not db:
            db = self.last_db
        if not collection:
            collection = self.last_collection

        dbmErrorHandler.CollectionError(collection)
        dbmErrorHandler.DataBaseError(db)
        dbmErrorHandler.ClientNameError(name)

        return deepcopy(self.clients[name]['databases'][db][collection]['data'])

    def pushOneData(self, data, collection=None, db=None, name=None):
        if not name:
            name = self.last_client
        if not db:
            db = self.last_db
        if not collection:
            collection = self.last_collection

        dbmErrorHandler.CollectionError(collection)
        dbmErrorHandler.DataBaseError(db)
        dbmErrorHandler.ClientNameError(name)
        dbmErrorHandler.DataError(data)
        dbmErrorHandler.DataPushWarning(data, name+"/"+db+"/"+collection)
        print (data)
        if data:
            self.getGivenCollection(collection, db, name).insert_one(data)


    def pushData(self, collection=None, db=None, name=None):
        if not name:
            name = self.last_client
        if not db:
            db = self.last_db
        if not collection:
            collection = self.last_collection

        dbmErrorHandler.CollectionError(collection)
        dbmErrorHandler.DataBaseError(db)
        dbmErrorHandler.ClientNameError(name)

        data = self.getCollectionData(collection, db, name)
        c_id = self.clients[name]['databases'][db][collection]['current_id']
        dbmErrorHandler.DataPushWarning(data[c_id:], name+"/"+db+"/"+collection)
        if self.getGivenCollection(collection, db, name).count() > 0:
            id = self.clients[name]['databases'][db][collection]['id'] - \
                (self.getGivenCollection(collection, db, name).count() - 1)
        else:
            id = self.clients[name]['databases'][db][collection]['id']
        if data:
            if c_id <= id:
                self.getGivenCollection(collection, db, name).insert_many(data[c_id:])
                self.clients[name]['databases'][db][collection]['current_id'] = id + 1

    def pullOneData(self, collection=None, db=None, name=None):
        if not name:
            name = self.last_client
        if not db:
            db = self.last_db
        if not collection:
            collection = self.last_collection

        dbmErrorHandler.CollectionError(collection)
        dbmErrorHandler.DataBaseError(db)
        dbmErrorHandler.ClientNameError(name)

        data_len = self.getGivenCollection(collection, db, name).count() - 1
        id = self.clients[name]['databases'][db][collection]['id']

        if data_len < 0 or id == data_len:
            dbmErrorHandler.DataPullWarning(name+"/"+db+"/"+collection)
        else:
            data = self.getGivenCollection(collection, db, name).find({"id":{'$gte':id, '%lte':id+1}})
            self.clients[name]['databases'][db][collection]['id'] = data_len
            for item in data:
                del item['_id']
                self.clients[name]['databases'][db][collection]['data'].append(item)

    def pullData(self, collection=None, db=None, name=None):
        if not name:
            name = self.last_client
        if not db:
            db = self.last_db
        if not collection:
            collection = self.last_collection

        dbmErrorHandler.CollectionError(collection)
        dbmErrorHandler.DataBaseError(db)
        dbmErrorHandler.ClientNameError(name)

        data_len = self.getGivenCollection(collection, db, name).count() - 1
        id = self.clients[name]['databases'][db][collection]['id']

        if data_len < 0 or id == data_len:
            dbmErrorHandler.DataPullWarning(name+"/"+db+"/"+collection)
        else:
            data = self.getGivenCollection(collection, db, name).find({"id":{'$gte':id}})
            self.clients[name]['databases'][db][collection]['id'] = data_len
            for item in data:
                del item['_id']
                self.clients[name]['databases'][db][collection]['data'].append(item)

    def addRunner(self, collection=None, db=None, name=None):
        if not name:
            name = self.last_client
        if not db:
            db = self.last_db
        if not collection:
            collection = self.last_collection

        dbmErrorHandler.CollectionError(collection)
        dbmErrorHandler.DataBaseError(db)
        dbmErrorHandler.ClientNameError(name)

        _runner = dict(
            id = len(self.runner),
            is_running = False,
            collection = collection,
            db = db,
            name = name,
            Thread = Thread(target=self.run)
        )

        self.runner.append(_runner)
        self.last_runner = _runner['id']

    def startAllRunner(self):
        for id in range(len(self.runner)):
            self.startRunner(id)

    def stopAllRunner(self):
        for id in range(len(self.runner)):
            self.stopRunner(id)

    def stopRunner(self, id):
        try:
            self.runner[id]['is_running'] = False
        except IndexError:
            dbmErrorHandler.RunnerExistWarning(id)

    def startRunner(self, id):
        try:
            if not self.runner[id]['is_running']:
                self.last_runner = id
                self.runner[id]['Thread'].start()
        except IndexError:
            dbmErrorHandler.RunnerExistWarning(id)

    def run(self, sleep=0.01):
        runner = self.runner[self.last_runner]
        collection = self.runner[runner['id']]['collection']
        db = self.runner[runner['id']]['db']
        name = self.runner[runner['id']]['name']
        self.runner[runner['id']]['is_running'] = True
        while self.runner[runner['id']]['is_running']:
            c_id = deepcopy(self.clients[name]['databases'][db][collection]['current_id'])
            len_d = deepcopy(len(self.clients[name]['databases'][db][collection]['data']) - 1)
            for idx in range(c_id+1, len_d):
                data = self.clients[name]['databases'][db][collection]['data'][idx]
                self.pushOneData(data, collection, db, name)
                self.clients[name]['databases'][db][collection]['current_id'] += 1
            time.sleep(sleep)

class dbmErrorHandler(object):
    def custom_warning(msg, *args, **kwargs):
        return  '\033[91m' + "Warning : " + str(msg) + '\033[0m' + '\n'

    def CollectionError(value):
        if not isinstance(value, str):
            raise TypeError("%s in not a valid type for collection it should be str" % type(value))

    def DataBaseError(value):
        if not isinstance(value, str):
            raise TypeError("%s in not a valid type for database it should be str" % type(value))

    def ClientError(value):
        if not isinstance(value, MongoClient):
            raise TypeError("%s in not a valid type for client it should be MongoClient" % type(value))

    def ClientNameError(value):
        if not isinstance(value, str):
            raise TypeError("%s in not a valid type for client name it should be str" % type(value))

    def DataError(value):
        if not isinstance(value, dict):
            raise TypeError("%s in not a valid type for data it should dict" % type(value))

    def DataPushWarning(value, loc):
        if len(value) == 0 or value == {}:
            warnings.warn("There is no data to push in {}".format(loc))

    def DataPullWarning(loc):
        warnings.warn("There is no data to pull in {}".format(loc))

    def RunnerExistWarning(runner):
        warnings.warn("This runner does not exist id: {}".format(runner))

warnings.formatwarning = dbmErrorHandler.custom_warning
