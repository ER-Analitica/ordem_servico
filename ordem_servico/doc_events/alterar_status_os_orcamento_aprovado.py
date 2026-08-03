from __future__ import unicode_literals
from pydoc import doc
import frappe
from frappe.utils import flt

def on_update_after_submit(self, method):
    previous = self.get_doc_before_save()

    if previous and previous.workflow_state == "Pendente de Aprovação" and self.workflow_state == "Aprovado" and self.os_interna_link and self.os_interna_link.strip() != "":
        os_doc = frappe.get_doc("Ordem Servico Interna", self.os_interna_link)
        os_doc.status_order_service = "Em Conserto"
        os_doc.save(ignore_permissions=True)


def on_cancel(self, method=None):
    """Reprovar o orçamento leva a OS de origem para 'Reprovado'.

    A transição 'Reprovar' do workflow leva o documento de docstatus 1 para 2,
    ou seja, passa por doc.cancel() — o on_update_after_submit não dispara aqui.
    A ação 'Cancelar' cai no mesmo gancho, por isso a checagem do estado.

    A gravação é direta no banco: rodar o validate completo da OS durante o
    cancelamento do orçamento poderia falhar por dados não relacionados e
    impedir a reprovação.
    """
    if self.workflow_state != "Reprovado":
        return

    if not (self.os_interna_link and self.os_interna_link.strip()):
        return

    os_name = self.os_interna_link.strip()
    if not frappe.db.exists("Ordem Servico Interna", os_name):
        return

    frappe.db.set_value(
        "Ordem Servico Interna", os_name, "status_order_service", "Reprovado"
    )
    frappe.clear_document_cache("Ordem Servico Interna", os_name)

    # Avisa em tempo real quem estiver com a OS aberta, para o status mudar na
    # tela sem precisar recarregar (o db.set_value sozinho não emite esse aviso,
    # diferente do doc.save() usado no fluxo de aprovação).
    try:
        frappe.get_doc("Ordem Servico Interna", os_name).notify_update()
    except Exception:
        pass




