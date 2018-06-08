## All passwords are temporary
import json
from flask import Flask, request
from sqlalchemy import create_engine
from flask_restful import Resource, Api
from databasetools.mongo import MongoCollection


class AuthenticationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Authentication:
    def __init__(self):
        self.authDB = MongoCollection('auth_db', "auth", indexOn=['login'],
                                      host='localhost', user=None, password=None, version='0.0.1')

    def authentify(self, login='', password=''):
        if login in self.authDB:
            if self.authDB[login]['password'] == password:
                return 2345678
            return -2
        return -1

    def register(self, login, password):
        if login and password:
            if login in self.authDB:
                return
            self.authDB.insert({'login': login, 'password': password})


if __name__ == '__main__':
    au = Authentication()
    au.register('Ajod', 'Renewal42')
    token = au.authentify('Ajod', 'Renewal42')
    if token == -1:
        raise AuthenticationError('Authentication failed: incorrect login')
    elif token == -2:
        raise AuthenticationError('Authentication failed: incorrect password')
    print("Authentified properly")
