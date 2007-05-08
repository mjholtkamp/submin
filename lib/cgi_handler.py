#!/usr/bin/python
import cgitb; cgitb.enable()
from dispatch.cgirequest import CGIRequest
from dispatch import dispatcher

req = CGIRequest()
dispatcher(req)