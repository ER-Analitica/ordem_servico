from __future__ import unicode_literals
import frappe
import requests
import json

from frappe.model.document import Document


def on_submit(self, method):
            url = "https://api.asaas.com/v3/customers?cpfCnpj="+str(frappe.db.get_value("Customer", self.customer, "cnpj"))
            payload={}
            headers = {
                'Content-Type': 'application/json',
                'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAyNjA5NzM6OiRhYWNoXzQ0YWMzZDRmLTE4NDEtNDY3Ny04NGFkLTQ0NzVjMDEwYTk4Mg==',
                'Cookie': 'AWSALB=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBCORS=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBTG=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; AWSALBTGCORS=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; JSESSIONID=8728B03FD2C0905324D8BB3AC2EBA48BA60307F616A5655CB8DCD23281D6FA3FCB1873C3D15F5B0DB19FFA284A4538196265212522502A348940AEC0BEB10BC2.n2'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
                
            print(response.text)
            datajson = json.loads(response.text)
            total = datajson.get("totalCount")
            if total != 0:

                id_customer = datajson['data'][0]
                self.id_cliente_asaas = id_customer['id']

                url = "https://api.asaas.com/v3/customers/"+str(self.id_cliente_asaas)

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
                headers = {
                'Content-Type': 'application/json',
                'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAyNjA5NzM6OiRhYWNoXzQ0YWMzZDRmLTE4NDEtNDY3Ny04NGFkLTQ0NzVjMDEwYTk4Mg==',
                'Cookie': 'AWSALB=zH4TGblJ8duV0rbahXrwUOm4U6Xu0IaoCiBu8lHyIuCbtFmEO95ojigs3sSTaNB5GWNdNXvDirtcBJB9b4vJdelytonj+3CFOBF19DJLS7HpyCAXXXKttOVUGY5E; AWSALBCORS=zH4TGblJ8duV0rbahXrwUOm4U6Xu0IaoCiBu8lHyIuCbtFmEO95ojigs3sSTaNB5GWNdNXvDirtcBJB9b4vJdelytonj+3CFOBF19DJLS7HpyCAXXXKttOVUGY5E; AWSALBTG=1cVi9QSdmm4+hru8tqck99zVxWsf+kglmejDeaoIvLpa5fkw5jT8M5tXLafTFkE6pWzxJDNi4RqvO500AIkG6WDpS1ljbcQcp/pA3IlMHYck46HsCaEjg5iCD2QGlDfNrDFwHTpR97+dZ/7iFs3lsaUrGebcY8+rlHMHsnl4hg/y; AWSALBTGCORS=1cVi9QSdmm4+hru8tqck99zVxWsf+kglmejDeaoIvLpa5fkw5jT8M5tXLafTFkE6pWzxJDNi4RqvO500AIkG6WDpS1ljbcQcp/pA3IlMHYck46HsCaEjg5iCD2QGlDfNrDFwHTpR97+dZ/7iFs3lsaUrGebcY8+rlHMHsnl4hg/y'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                print(response.text)
