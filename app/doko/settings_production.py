import os
from .settings import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = os.environ['SECRET_KEY']
