import xml.etree.ElementTree as ET
import frappe

from frappe.utils.file_manager import get_file_path

@frappe.whitelist()
def process_xml(doc, method):
     
    try:
        count = 0
        while count < 3:
            os = frappe.new_doc("Ordem Servico Interna")
            os.customer = doc.cliente
            os.equipment_location = ""
            os.contact_link = ""
            os.save()
            count += 1

        # Obtenha o caminho do arquivo XML
        file_path = get_file_path(doc.xml)

        # Verifique se o caminho do arquivo é uma string e se não está vazio
        if not isinstance(file_path, str) or not file_path:
            raise ValueError("O caminho do arquivo não é válido.")

        # Parse o arquivo XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extrair todo o texto do XML
        '''
        texto = ""
        for elem in root.iter():
            if elem.text:
                texto += elem.text.strip() + "\n"

        # Armazene a informação no campo doc.texto
        doc.texto_xml = texto.strip()
        '''
        
    
    except FileNotFoundError:
        frappe.throw("O arquivo XML não foi encontrado.")
    except ValueError as e:
        frappe.throw(f"Erro de valor: {str(e)}")
    except ET.ParseError:
        frappe.throw("Erro ao processar o XML. O arquivo pode estar corrompido ou mal formatado.")
    except Exception as e:
        frappe.throw(f"Erro ao processar o XML: {str(e)}")
