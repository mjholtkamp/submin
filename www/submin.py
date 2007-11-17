#!/usr/bin/python
import sys
sys.path.append('../lib/')
import cgitb; cgitb.enable()
from dispatch.cgirequest import CGIRequest
from dispatch import dispatcher

req = CGIRequest()
dispatcher(req)

