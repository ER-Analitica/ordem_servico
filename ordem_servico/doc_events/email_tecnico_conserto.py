"""Registra o e-mail do técnico que finalizou o conserto.

O nome já é gravado em `repaired_by_name2` quando o técnico clica em
"Finalizar Manutenção". Este gancho captura, no mesmo momento, o e-mail do
usuário da sessão — que é o próprio técnico.

A captura acontece só na transição (quando `end_repair_time` passa a existir):
depois disso o valor é preservado, para que um save feito por outra pessoa
não sobrescreva o responsável real.
"""

import frappe


def capturar_email_tecnico(doc, method=None):
    if not doc.get("end_repair_time"):
        return

    # Não sobrescreve um e-mail já registrado
    if doc.get("repaired_by_email"):
        return

    anterior = doc.get_doc_before_save()
    acabou_de_finalizar = not anterior or not anterior.get("end_repair_time")
    if not acabou_de_finalizar:
        return

    email = frappe.db.get_value("User", frappe.session.user, "email")
    if email:
        doc.repaired_by_email = email
