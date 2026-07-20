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
    "Employee": [
        {
            "fieldname": "custom_escolaridade",
            "fieldtype": "Select",
            "label": "Escolaridade",
            "options": (
                "\nEnsino fundamental incompleto\nEnsino fundamental completo"
                "\nEnsino médio incompleto\nEnsino médio completo"
                "\nEnsino superior incompleto\nEnsino superior completo"
            ),
            "insert_after": "date_of_birth",
        },
    ],
}


def setup_custom_fields():
    create_custom_fields(CUSTOM_FIELDS, update=True)
