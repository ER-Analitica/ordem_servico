frappe.ui.form.on('Event', {
    iniciar_cronometro: function () {
        frappe.call({
            method: 'ordem_servico.ordem_servico.event_document.start_maintenance',
            args: {
                docname: frm.doc.name,
            },
        });
    },

});