#!/usr/bin/python
import sys
sys.path.append('../lib/')
from models import backend

backend.open()

import cgitb; cgitb.enable()
from dispatch.cgirequest import CGIRequest
from dispatch import dispatcher

req = CGIRequest()
response = dispatcher(req)
req.writeResponse(response)

backend.close()
