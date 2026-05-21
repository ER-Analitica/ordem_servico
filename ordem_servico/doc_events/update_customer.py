from __future__ import unicode_literals
import frappe
import requests
import json

from frappe.model.document import Document

ASAAS_TOKEN = "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmEwZDhkY2UzLWYwYjEtNDY1Zi1iMDc2LTY3NDEwOTAzZTkwNTo6JGFhY2hfM2M3ZmRmYzktM2EzOS00NWNjLTgwMjgtZmU3ZjU0Y2JlMTZl"
ASAAS_SANDBOX = True  # Alterar para False ao ir para produção
ASAAS_BASE_URL = "https://api-sandbox.asaas.com/v3" if ASAAS_SANDBOX else "https://api.asaas.com/v3"


def on_submit(self, _method):
    headers = {
        'Content-Type': 'application/json',
        'access_token': ASAAS_TOKEN,
    }

    cnpj = frappe.db.get_value("Customer", self.customer, "cnpj")
    url = f"{ASAAS_BASE_URL}/customers?cpfCnpj={cnpj}"

    response = requests.request("GET", url, headers=headers)
    datajson = json.loads(response.text)

    if not datajson.get("data"):
        return

    id_cliente = datajson['data'][0]['id']
    self.id_cliente_asaas = id_cliente

    url_update = f"{ASAAS_BASE_URL}/customers/{id_cliente}"
    payload = json.dumps({
        "name": frappe.db.get_value("Customer", self.customer, "customer_name"),
        "email": frappe.db.get_value("Contact", self.contact_person, "email_id"),
        "phone": frappe.db.get_value("Contact", self.contact_person, "phone"),
        "mobilePhone": frappe.db.get_value("Contact", self.contact_person, "mobile_no"),
        "postalCode": frappe.db.get_value("Address", self.customer_address, "cep"),
        "address": frappe.db.get_value("Address", self.customer_address, "address_line1"),
        "addressNumber": frappe.db.get_value("Address", self.customer_address, "numero"),
        "complement": frappe.db.get_value("Address", self.customer_address, "address_line2"),
        "province": frappe.db.get_value("Address", self.customer_address, "bairro"),
    })

    response_update = requests.request("POST", url_update, headers=headers, data=payload)
    datajson_update = json.loads(response_update.text)

    if datajson_update.get("errors"):
        frappe.log_error(title="Asaas Update Customer Error", message=response_update.text)
        frappe.throw(f"Erro ao atualizar cliente no Asaas: {response_update.text}")
