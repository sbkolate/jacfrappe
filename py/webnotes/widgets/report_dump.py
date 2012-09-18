# Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
# 
# MIT License (MIT)
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from __future__ import unicode_literals
import webnotes
import json

@webnotes.whitelist()
def get_data():
	from startup.report_data_map import data_map
	from webnotes.utils import cstr
	
	doctypes = json.loads(webnotes.form_dict.get("doctypes"))
	out = {}
	for d in doctypes:
		args = data_map[d]
		conditions = order_by = ""
		if args.get("conditions"):
			conditions = " where " + " and ".join(args["conditions"])
		if args.get("order_by"):
			order_by = " order by " + args["order_by"]
		
		out[d] = {}
		out[d]["data"] = webnotes.conn.sql("""select %s from `tab%s` %s %s""" % (",".join(args["columns"]),
			d, conditions, order_by), as_list=1)
		out[d]["columns"] = map(lambda c: c.split(" as ")[-1], args["columns"])
		
		if args.get("links"):
			out[d]["links"] = args["links"]
	
	for d in out:
		if out[d].get("links"):
			for link_key in out[d]["links"]:
				link = out[d]["links"][link_key]
				if link[0] in out:
					
					# make a map of link ids
					# to index
					link_map = {}
					doctype_data = out[link[0]]
					col_idx = doctype_data["columns"].index(link[1])
					for row_idx in xrange(len(doctype_data["data"])):
						row = doctype_data["data"][row_idx]
						link_map[row[col_idx]] = row_idx
						
					for row in out[d]["data"]:
						col_idx = out[d]["columns"].index(link_key)
						# replace by id
						row[col_idx] = link_map[row[col_idx]]
						
	#for d in out:
	#	out[d]["data"] = "~".join(["|".join([cstr(e) for e in p]) for p in out[d]["data"]])
	
	return out
