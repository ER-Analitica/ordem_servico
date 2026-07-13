from __future__ import unicode_literals


def calcular_total_tempo_execucao(doc, method=None):
    total_segundos = sum(
        (item.custom_custom_tempo_de_execucao or 0) * (item.qty or 0)
        for item in (doc.items or [])
    )
    if total_segundos:
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        doc.custom_total_tempo_de_execucao_servico = (
            f"{horas}h {minutos}m" if minutos else f"{horas}h"
        )
    else:
        doc.custom_total_tempo_de_execucao_servico = ""
