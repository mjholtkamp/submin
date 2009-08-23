#!/usr/bin/python
import sys
import os
# __file__ contains <submin-dir>/www/submin.cgi
submindir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(submindir, 'lib'))
from models import backend

backend.open()

import cgitb; cgitb.enable()
from dispatch.cgirequest import CGIRequest
from dispatch import dispatcher

req = CGIRequest()
response = dispatcher(req)
req.writeResponse(response)

backend.close()
