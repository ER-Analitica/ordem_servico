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
web_include_js = [
    "/assets/ordem_servico/datatables/dataTables.min.js"
]

web_include_css = [
    "/assets/ordem_servico/datatables/dataTables.min.css"
]

doctype_js = {
    #"Customer" : "public/js/jquery.mask.min.js",
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
             'Customer',
             'Client Script',
             'Opportunity',
             'Payment Schedule',
             'Payment Term',
             'Purchase Order',
             'Employee',
             'Employee Education',
             'Designation',
             'Letter Head',
             'Quality Feedback Parameter',
             'Supplier',
             'Request for Quotation',
             'Request for Quotation Item',
             'Company'
             
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
             'Customer',
             'Client Script',
             'Opportunity',
             'Payment Schedule',
             'Payment Term',
             'Purchase Order',
             'Employee',
             'Employee Education',
             'Designation',
             'Letter Head',
             'Quality Feedback Parameter',
             'Supplier',
             'Request for Quotation',
             'Request for Quotation Item',
             'Company'
             
         )
     ]]
     },
     {
         "dt":"Client Script"
     },

     {
         "dt":"Server Script"
     },

     {
         "dt":"Web Page"
     },
    
]
doc_events = {
    "Customer": {
        "validate": [
            "ordem_servico.doc_events.customer.validate",
            "ordem_servico.doc_events.data_limite_dn.data_limite_dn",
            "ordem_servico.doc_events.data_limite_pv.data_limite_pv"
        ]
    }, 
    "Sales Invoice": {
        "on_submit": "ordem_servico.doc_events.update_customer.on_submit",
        "validate": [
            "ordem_servico.doc_events.termo_pagamento_dn.validate",
        ]
    },
    

    "Delivery Note":{
        "validate":[
            "ordem_servico.doc_events.termo_pagamento_si.validate",
        ]
    },
  
    "Item Price":{
        "on_update": "ordem_servico.doc_events.update_item.on_update",
    },
    "ToDo":{
        "on_update": "ordem_servico.doc_events.update_data_vencimento.update_data_vencimento",
    },
    "Quotation":{
        "validate": "ordem_servico.doc_events.limpar_hash.validate",
    },
    
    "Criador de Ordens de Servico em Lote":{
        #"on_submit": "ordem_servico.doc_events.criador_de_ordens_de_servico_em_lote.on_submit",
        #o doc_events comentado será utilizado quando estiver pronto o formulário de visita caso o hooks suba para produção sem ainda ter o formulário de visita
        #é necessário comentar a linha 164
        "before_submit": "ordem_servico.doc_events.criador_de_ordens_de_servico_em_lote.before_submit",
    },
    "Employee":{
        "validate": [
            "ordem_servico.doc_events.data_validade_colaborador.validate",
            "ordem_servico.doc_events.sem_data_validade.validate",
            "ordem_servico.doc_events.atualiza_status_com_base_data_documentos_colaborador.validate",

        ]
    },
    "Sales Order": {
        "on_submit": "ordem_servico.doc_events.analise_critica_campos_vazios.analise_critica_campos_vazios",
        "validate":[
             "ordem_servico.doc_events.analise_critica_customer.pegar_valor_cliente",
             "ordem_servico.doc_events.obter_pedido_os_interna_atraves_da_so.obter_pedido_os_interna_atraves_da_so",
        ],
        
    },

    "Ordem Servico Interna": {
        "validate":[
             "ordem_servico.doc_events.validacao_equipamento_ordem_servico.validacao_equipamento_ordem_servico",
             "ordem_servico.doc_events.obter_pedido_os_interna.obter_pedido_os_interna",
        ]
    },

    "Ordem Servico Externa": {
        "validate":[
             "ordem_servico.doc_events.validacao_equipamento_ordem_servico.validacao_equipamento_ordem_servico",
        ]
    }


    #"Ordem Servico Interna":{
    #    "validate": "ordem_servico.doc_events.validar_equip.validate",
    #}

    
    #"Criador de Ordem de Servico Por XML": {
       #"validate": [
           #"ordem_servico.doc_events.xml.process_xml",
           #"ordem_servico.doc_events.pypdf2.process_pdf",
           #"ordem_servico.doc_events.ocr.process_image"
       #]
    #},
    
    
    #"Contact": {
     #   "before_save": "ordem_servico.doc_events.update_contact.before_save",
        
    #},
    


    
}




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