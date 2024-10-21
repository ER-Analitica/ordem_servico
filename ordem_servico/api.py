# -*- coding: utf-8 -*-

from requests.structures import CaseInsensitiveDict
import requests
import frappe
import re




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
@frappe.whitelist()
def get_cnpj(cnpj):
    resp = requests.get('https://publica.cnpj.ws/cnpj/{cnpj}'.format(cnpj=re.sub('[/.-]','',cnpj))) 
   
    if resp.status_code == 200:
            json = resp.json()
            print('CNPJ Consultado')
            return {
              "customer_name" : json['razao_social'],
              "nome_fantasia": json['estabelecimento']['nome_fantasia']
            
            }
    elif resp.status_code == 404:
            
            return {
              
              "cnpj" : ""
              
              
            }

@frappe.whitelist()
def get_transaction_list(
    doctype,
    txt=None,
    filters=None,
    limit_start=None,
    limit_page_length=20,
    order_by='creation',
    custom=False):

    from erpnext.controllers.website_list_for_contact import get_transaction_list

    return get_transaction_list(
        doctype=doctype,
        txt=txt,
        filters=filters,
        limit_start=limit_start,
        limit_page_length=limit_page_length,
        order_by=order_by,
        custom=custom
    )

                  
            
            
            
            
            
           
            

          
    return {}

  

 

 



















