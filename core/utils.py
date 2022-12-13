from django.db.models import Q
from django.shortcuts import get_object_or_404
from accounts.models import User
from pathlib import Path
import random
import string
import datetime
import pathlib
import json

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))