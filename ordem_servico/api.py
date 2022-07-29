import requests
import frappe

@frappe.whitelist()
def get_cep(cep):
  
    print('Consultando CEP')

    res = requests.get('https://viacep.com.br/ws/{cep}/json/'.format(cep=cep)) 
    if res.status_code == 200:
        json = res.json()
        print('CEP Consultado')
        return {
          "cep": json['cep'],
          "address_line1": json['logradouro'],
          "bairro": json['bairro'],
          "city": json['localidade'],
          "uf": json['uf'],
          "ibge": json['ibge'],
          "address_line2": json.get('complemento')
        }  
    return {}




 



















