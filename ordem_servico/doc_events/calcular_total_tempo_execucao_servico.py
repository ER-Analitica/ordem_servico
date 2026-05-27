from __future__ import unicode_literals

from frappe.utils import format_duration


def calcular_total_tempo_execucao(doc, method=None):
    total_segundos = sum(
        (item.custom_custom_tempo_de_execucao or 0) * (item.qty or 0)
        for item in (doc.items or [])
    )
    doc.custom_total_tempo_de_execucao_servico = (
        format_duration(total_segundos) if total_segundos else ""
    )
