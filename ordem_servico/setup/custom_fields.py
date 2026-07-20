from __future__ import unicode_literals

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
    "Supplier": [
        {
            "fieldname": "custom_homologacao",
            "fieldtype": "Select",
            "label": "Homologação",
            "options": "Sim\nNão\nNA/Dispensado",
            "insert_after": "is_transporter",
        },
    ],
}


def setup_custom_fields():
    create_custom_fields(CUSTOM_FIELDS, update=True)
