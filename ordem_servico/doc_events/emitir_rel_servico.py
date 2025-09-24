from __future__ import unicode_literals
import frappe
from datetime import datetime

def on_update_after_submit(doc, method):
    if doc.emitir_rel_servico == "EMITIR RELATÓRIO":
        doc.emitir_rel_servico = "RELATÓRIO EMITIDO"

        data_mais_recente = None
        ultimo_tecnico = None
        os_sem_inicio = []  # Lista para OS sem data de início
        os_sem_fim = []  # Lista para OS sem data de finalização
        os_sem_servico = []  # Lista para OS sem nenhum serviço marcado

        for relatorio_servico in doc.equipamentos_relatorio_servico:
            os_externa_relacionada = relatorio_servico.os_rel_servico

            if os_externa_relacionada:
                os_externa_doc = frappe.get_doc("Ordem Servico Externa", os_externa_relacionada)

                # Preenchendo os campos do relatório de serviço
                relatorio_servico.equipamento_rel_servico = os_externa_doc.equipment_description 
                relatorio_servico.equipment_model_rel_servico = os_externa_doc.equipment_model
                relatorio_servico.marca_rel_servico = os_externa_doc.marca_equipamento 
                relatorio_servico.numero_serie_rel_servico = os_externa_doc.serie_number
                relatorio_servico.identif_cliente_rel_servico = os_externa_doc.equipment_tag
                relatorio_servico.obs_rel_servico = os_externa_doc.repair_observation
                relatorio_servico.repair_status = os_externa_doc.repair_status
                relatorio_servico.cal_rbc_rel = os_externa_doc.cal_rbc
                relatorio_servico.cal_rastreavel_rel = os_externa_doc.cal_rastreavel
                relatorio_servico.man_prev_rel = os_externa_doc.manutencao_preventiva
                relatorio_servico.man_corretiva_rel = os_externa_doc.manutencao_corretiva
                relatorio_servico.qualificacao_rbc_temperatura_rel = os_externa_doc.qualificacao_temperatura
                relatorio_servico.troca_pecas_rel = os_externa_doc.troca_pecas
                relatorio_servico.quais_pecas_rel = os_externa_doc.quais_pecas

                ultimo_tecnico = os_externa_doc.repaired_by_name2

                # Verifica se pelo menos um serviço foi marcado
                if not any([
                    os_externa_doc.cal_rbc,
                    os_externa_doc.cal_rastreavel,
                    os_externa_doc.manutencao_preventiva,
                    os_externa_doc.manutencao_corretiva,
                    os_externa_doc.qualificacao_temperatura,
                    os_externa_doc.troca_pecas,
                    os_externa_doc.repair_observation
                ]):
                    os_sem_servico.append(os_externa_relacionada)

                # Tratamento da data de início
                try:
                    if os_externa_doc.start_repair_time:
                        data_inicio_os = datetime.strptime(os_externa_doc.start_repair_time, "%d-%m-%Y %H:%M:%S")
                        data_inicio = data_inicio_os.strftime('%d/%m/%Y')
                        doc.data_inicio = data_inicio
                    else:
                        os_sem_inicio.append(os_externa_relacionada)
                except Exception:
                    os_sem_inicio.append(os_externa_relacionada)

                # Tratamento da data de finalização
                try:
                    if os_externa_doc.end_repair_time:
                        data_finalizacao = datetime.strptime(os_externa_doc.end_repair_time, "%d-%m-%Y %H:%M:%S")
                        if data_mais_recente is None or data_finalizacao > data_mais_recente:
                            data_mais_recente = data_finalizacao
                            doc.termino = data_mais_recente.strftime('%d/%m/%Y')
                            doc.termino_tipo_data = data_mais_recente.strftime('%Y-%m-%d')
                            doc.responsavel_tecnico = ultimo_tecnico
                    else:
                        os_sem_fim.append(os_externa_relacionada)
                except Exception:
                    os_sem_fim.append(os_externa_relacionada)

                relatorio_servico.save()

        doc.save()

        # Construir a mensagem de erro consolidada
        mensagem_erro = ""

        if os_sem_inicio:
            os_inicio_list = ", ".join(os_sem_inicio)
            mensagem_erro += f"<b>OS não iniciada:</b><br>{os_inicio_list}<br><hr>"

        if os_sem_fim:
            os_fim_list = ", ".join(os_sem_fim)
            mensagem_erro += f"<b>OS não finalizada:</b><br>{os_fim_list}<br><hr>"

        if os_sem_servico:
            os_servico_list = ", ".join(os_sem_servico)
            mensagem_erro += f"<b>As seguintes Ordens de Serviço apresentam informações incompletas:</b><br>{os_servico_list}<br><br> <b>Verifique as seguintes pendências antes de prosseguir:<br> - A OS não possui nenhuma observação registrada <br> - Nenhum serviço foi marcado como realizado. <b/>"

        # Lança um erro se houver alguma OS sem início, sem finalização ou sem serviço marcado
        if mensagem_erro:
            frappe.throw(mensagem_erro)
