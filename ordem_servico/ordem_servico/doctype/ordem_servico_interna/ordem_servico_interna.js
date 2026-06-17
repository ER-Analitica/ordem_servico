// Copyright (c) 2018, laugusto and contributors
// For license information, please see license.txt

{% include 'ordem_servico/public/js/ordem_servico.js' %}

frappe.ui.form.on('Ordem Servico Interna', {
  validate(frm){
    if (frm.doc.problem_description && frm.doc.problem_description.length){
      frm.set_value("problem_description", frm.doc.problem_description.replaceAll("img src=", 'img style="max-width:300px !important; max-height:300px !important; width: auto; height: auto;" src='));
    }
    if (frm.doc.informe_numero_serie && !frm.doc.grandeza){
      frappe.msgprint({
        title: "Campo obrigatório",
        message: "O campo <b>Grandeza</b> é obrigatório quando um equipamento está selecionado.",
        indicator: "red"
      });
      frappe.validated = false;
    }
  },
  customer(frm) {
		var me = this;
		erpnext.utils.get_party_details(frm, null, null, function() {
			me.apply_price_list();
		});
	},

  refresh: function(frm) {

    let equipamento_field = frm.get_docfield("informe_numero_serie");

    // Substitui o comportamento de criação de novo documento
    equipamento_field.get_route_options_for_new_doc = function(row) {
        if (frm.is_new()) return; // não faz nada se a OS ainda não estiver salva

        // Preenche o campo customer do novo Equipamento com o valor da OS
        return {
            "customer": frm.doc.customer,
            "contact_link": frm.doc.contact_link
        };
    };
},
  
  /*address_os: function(frm) {
    erpnext.utils.get_address_display(frm, "address_os", "address_display");
  },*/
  
  before_save(frm) {
    if (frm.doc.status_order_service === 'Encerrada')
      frm.events.finish_maintenance(frm)
  },
  schedule_quotation_event(frm) {
    const { __unsaved } = cur_frm.doc
    if (__unsaved) {
      frappe.throw('Favor salvar documento!')
    }
    const {
      doctype,
      name,
      quotation_schedule_date,
      quotation_schedule_time,
      quotation_time
    } = frm.doc
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.make_event',
      args: {
        doctype: doctype,
        docname: name,
        start_date: quotation_schedule_date,
        start_time: quotation_schedule_time,
        work_time: quotation_time,
        trigger: 'quotation'
      },
      callback(res){
        show_alert('Orçamento agendado.')
        frm.reload_doc()
      }
      
    })
  },
  start_quotation(frm) {
    const { __unsaved } = cur_frm.doc
    if (__unsaved) {
      frappe.throw('Favor salvar documento!')
    }
    const { doctype, name } = frm.doc
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.get_time_now',
      args: {
        doctype: doctype,
        docname: name,
        trigger: 'start_quotation'
      },
      callback(res){
        show_alert('Orçamento iniciado.')
        frm.reload_doc()
      }
    })
    
  },
  end_quotation(frm) {
    const { __unsaved } = cur_frm.doc
    if (__unsaved) {
      frappe.throw('Favor salvar documento!')
    }
    const { doctype, name } = frm.doc
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.get_time_now',
      args: {
        doctype: doctype,
        docname: name,
        trigger: 'end_quotation'
      },
      callback(res){
        show_alert('Orçamento finalizado.')
        frm.reload_doc()
      }
    })
  },
  create_quotation(frm) {
    const { __unsaved } = frm.doc
    if (__unsaved) {
      frappe.throw(__('You have unsaved changes in this form. Please save before you continue.'))
    }
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.make_quotation',
      args: {
        os_docname: frm.doc.name
      },
      callback(r) {
        frappe.model.sync(r.message)
        const { doctype, name } = r.message
        frappe.set_route('Form', doctype, name)
      }
    })
  },
  schedule_repair_event(frm) {
    const { __unsaved } = cur_frm.doc
    if (__unsaved) {
      frappe.throw('Favor salvar documento!')
    }
    const {
      doctype,
      name,
      repair_schedule_date,
      repair_schedule_time,
      repair_time
    } = frm.doc
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.make_event',
      args: {
        doctype: doctype,
        docname: name,
        start_date: repair_schedule_date,
        start_time: repair_schedule_time,
        work_time: repair_time,
        trigger: 'repair'
      },
      callback(res){
        show_alert('Conserto agendado.')
        frm.reload_doc()
      }
    })
  },
  start_repair(frm) {
    const { __unsaved } = cur_frm.doc
    if (__unsaved) {
      frappe.throw('Favor salvar documento!')
    }
    const { doctype, name } = frm.doc
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.get_time_now',
      args: {
        doctype: doctype,
        docname: name,
        trigger: 'start_repair'
      },
      callback(res){
        show_alert('Conserto iniciado.')
        frm.reload_doc()
      }
    })
  },
  end_repair(frm) {
    const { __unsaved, quotation_status } = cur_frm.doc
    if (__unsaved) {
      frappe.throw('Favor salvar documento!')
    }
    else if (!quotation_status) {
			frappe.throw('Favor colocar Status do Orçamento!')
		}
    else{
    const { doctype, name } = frm.doc
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.get_time_now',
      args: {
        doctype: doctype,
        docname: name,
        trigger: 'end_repair'
      },
      callback(res){
        show_alert('Conserto finalizado.')
        frm.reload_doc()
      }
    })
  }
  },
  finish_maintenance(frm) {
    const fields = frm.doc.accessories.map(item => ({
      fieldtype: 'Check', label: item.description
    }))
    const d = new frappe.ui.Dialog({
      title: 'Acessórios',
      fields: fields,
      primary_action_label: 'Confirmar',
      primary_action: (values) => {
        frm.events._validateAccessories(values)
        d.hide()
      },
      secondary_action_label: 'Fechar'
    })
    d.show()
  },
  _validateAccessories(values) {
    const isValid = Object.values(values).every(val => val)
    if (!isValid) frappe.throw('É necessário devolver todos os acessórios!')
  },
  equipment(frm){
    if (!frm.doc.equipment) return;
    frappe.model.get_value("Equipamentos do Cliente", 
    frm.doc.equipment, ["serie_number", "equipment_model", "tag", "description"], 
    function(res){
    [["serie_number","serie_number"], 
    ["equipment_model", "equipment_model"], 
    ["tag", "equipment_tag"], 
    ["description", "equipment_description"]].forEach(kv => {
    frm.set_value(kv[1], res[kv[0]]);
  })
  })
},
  informe_numero_serie(frm){
    // Protege a grandeza ao trocar de equipamento. O fetch_from limpa o campo
    // quando o equipamento não tem grandeza cadastrada; aqui restauramos o
    // valor anterior (vindo do Criador em Lote ou de preenchimento manual).
    // Prioridade: 1º grandeza do equipamento (fetch) / 2º grandeza já na OS / 3º vazio.
    let grandeza_anterior = frm.doc.grandeza;
    setTimeout(function(){
      if (!frm.doc.grandeza && grandeza_anterior){
        frm.set_value("grandeza", grandeza_anterior);
      }
    }, 500);
  },




})

