from __future__ import unicode_literals

import frappe


def before_submit(doc, method):
     
    try:
        if doc.ordem_servico == "Ordem Servico Externa" and doc.escolher_como_criar_osexterna == 'Referência do Pedido de Venda':
            
            item_codes_group = frappe.get_all(
                'Item',
                filters={
                    'item_group': ['in', ['Calibração Acreditada RBC', 'Calibração Rastreável']]
                },
                pluck='name'
            )

            item_codes_service = frappe.get_all(
                'Item',
                filters={
                    'criar_ordem_servico': 1
                },
                pluck='name'
            )

            # Unindo as listas de códigos de itens
            item_codes = list(set(item_codes_group) | set(item_codes_service))

            # Obtendo os itens da Sales Order Item que correspondem aos códigos filtrados
            items = frappe.get_all(
                'Sales Order Item',
                filters={
                    'parent': doc.sales_order_reference,
                    'item_code': ['in', item_codes]
                },
                fields=['item_name', 'item_code', 'qty', 'item_group']
            )

            quantidade_total = sum(item['qty'] for item in items)
            print(quantidade_total)
            count = 0
            #while count < quantidade_total:
            for item in items:
                for _ in range(int(item['qty'])):
                    
                    # Cria uma nova Ordem de Serviço
                    os = frappe.new_doc(doc.ordem_servico)
                    
                    # Preenchendo os campos necessários
                    os.customer = doc.cliente
                    os.contact_link = doc.contato
                    os.status_order_service = doc.status_order_service
                    os.sales_order_reference = doc.sales_order_reference
                    
                    # Salva a nova OS
                    os.save()

                    # Adiciona a OS criada na tabela interna
                    adiciona_os = doc.append("os_interna_table", {})
                    adiciona_os.os = os.name
                    adiciona_os.equipamento = item.item_name
                    adiciona_os.tipo_servico = item.item_group
                    if adiciona_os.tipo_servico == "Calibração Rastreável":
                        adiciona_os.cal_rastr = 1
                    if adiciona_os.tipo_servico == "Calibração Acreditada RBC":
                        adiciona_os.cal_rbc = 1
                    adiciona_os.preventiva = 1

                    # Adiciona a OS criada na tabela de equipamentos relatório de serviço
                    adiciona_os_rel = doc.append("equipamentos_relatorio_servico", {})
                    adiciona_os_rel.os_rel_servico = os.name

                    count += 1

        elif doc.ordem_servico == "Ordem Servico Externa" and doc.escolher_como_criar_osexterna == 'Quantidade':
            count = 0
            while count < int(doc.quantidade):
                os = frappe.new_doc(doc.ordem_servico)
                os.customer = doc.cliente
                os.contact_link = doc.contato
                os.status_order_service = doc.status_order_service
                os.sales_order_reference = doc.sales_order_reference
                os.save()
                adiciona_os = doc.append("os_interna_table", {})
                adiciona_os.os = os.name
                 # Adiciona a OS criada na tabela de equipamentos relatório de serviço
                adiciona_os_rel = doc.append("equipamentos_relatorio_servico", {})
                adiciona_os_rel.os_rel_servico = os.name
                count += 1
               

                
        elif doc.ordem_servico == "Ordem Servico Interna":
            count = 0
            while count < int(doc.quantidade):
                os = frappe.new_doc(doc.ordem_servico)
                os.customer = doc.cliente
                os.equipment_location = doc.loc_equip
                os.contact_link = doc.contato
                os.has_quotation_link = doc.orcamento
                os.have_quotation = doc.possui_orcamento
                os.status_order_service = doc.status_order_service_interna
                os.modalidade_entrada = doc.modalidade_entrada
                os.nome_transportadora_entrada = doc.nome_transportadora_entrada
                os.outro = doc.outro
                os.base_total = doc.base_total
                os.entry_date = doc.entry_date
                os.entry_sales_invoice = doc.entry_sales_invoice
                os.valor = doc.valor
                os.peso = doc.peso
                os.initial_scheduled_to = doc.initial_scheduled_to
                os.initial_scheduled_to_name = doc.initial_scheduled_to_name
                os.initial_scheduled_by_name = doc.initial_scheduled_by_name
                os.quotation_schedule_date = doc.quotation_schedule_date
                os.quotation_schedule_time = doc.quotation_schedule_time
                os.quotation_time = doc.quotation_time
                os.quotation_event_link = doc.quotation_event_link   
                os.os_items = doc.os_items
                os.pontos_cal_criterios_aceitacao = doc.pontos_cal_criterios_aceitacao
                os.final_scheduled_to = doc.final_scheduled_to
                os.final_scheduled_to_name = doc.final_scheduled_to_name
                os.final_scheduled_by_name = doc.final_scheduled_by_name
                os.repair_schedule_date = doc.repair_schedule_date
                os.repair_schedule_time = doc.repair_schedule_time
                os.repair_time = doc.repair_time
                os.repair_event_link = doc.repair_event_link
                os.save()
                count += 1
        
    except:
        frappe.throw("Ocorreu algum erro durante a criação em lote")
