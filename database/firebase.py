# Importe le module firebase_admin nécessaire pour l'initialisation de Firebase
import firebase_admin

from firebase_admin import credentials

import pyrebase

from configs.firebase_config import firebase_config

if not firebase_admin._apps:

    # auth information
    cred = credentials.Certificate("configs/config_key.json")

    # firebase 
    firebase_admin.initialize_app(cred)

firebase = pyrebase.initialize_app(firebase_config)

db = firebase.database()
authStudent = firebase.auth()
