# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "ordem_servico"
app_title = "Ordem Servico"
app_publisher = "laugusto"
app_description = "_"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "laugusto@eucon.tech"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ordem_servico/css/ordem_servico.css"
# app_include_js = "/assets/ordem_servico/js/ordem_servico.js"

# include js, css files in header of web template
# web_include_css = "/assets/ordem_servico/css/ordem_servico.css"
# web_include_js = "/assets/ordem_servico/js/ordem_servico.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
    "Ordem Servico Interna": "public/js/os_items.js",
    "Ordem Servico Externa": "public/js/os_items.js",
    "Quotation": "public/js/quotation.js",
    "Payment Entry": "public/js/payment_entry.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Sales Order": "public/js/sales_order.js",
    "Delivery Note": "public/js/delivery_note.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
fixtures = [
    {"dt": "Custom Field",
     "filters": [[
         "dt", "in", (
             'Delivery Note',
             'Event',
             'Item',
             'Payment Entry',
             'Quotation Item',
             'Quotation',
             'Sales Invoice',
             'Sales Order',
             'Address',
             'Purchase Order Item',
             'Customer'
             
         )
     ]]
     },
     {"dt": "Property Setter",
     "filters": [[
         "doc_type", "in", (
             'Delivery Note',
             'Event',
             'Item',
             'Payment Entry',
             'Quotation Item',
             'Quotation',
             'Sales Invoice',
             'Sales Order',
             'Address',
             'Purchase Order Item',
             'Customer'
             
         )
     ]]
     },
]
# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "ordem_servico.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "ordem_servico.install.before_install"
# after_install = "ordem_servico.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ordem_servico.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ordem_servico.tasks.all"
# 	],
# 	"daily": [
# 		"ordem_servico.tasks.daily"
# 	],
# 	"hourly": [
# 		"ordem_servico.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ordem_servico.tasks.weekly"
# 	]
# 	"monthly": [
# 		"ordem_servico.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "ordem_servico.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ordem_servico.event.get_events"
# }
