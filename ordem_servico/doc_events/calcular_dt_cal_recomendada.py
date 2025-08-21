import frappe
from datetime import datetime, timedelta

def calcular_dt_cal_recomendada(doc, method):
    if doc.data_cal:  # verifica se o campo tem data preenchida
        try:
            # Garante que o valor é um objeto date
            if isinstance(doc.data_cal, str):
                data_cal = datetime.strptime(doc.data_cal, "%Y-%m-%d").date()
            else:
                data_cal = doc.data_cal

            # Soma 365 dias
            data_cal_recomendada = data_cal + timedelta(days=365)

            # Joga no campo de destino
            doc.data_cal_recomendada = data_cal_recomendada

        except Exception as e:
            frappe.throw(f"Erro ao calcular nova data: {str(e)}")
