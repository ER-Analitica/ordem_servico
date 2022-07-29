frappe.ui.form.on("Address", "cep", function (frm) { 
    if (!frm.doc.cep) 
    return; 
frappe.call({ 
    method: 'ordem_servico.api.get_cep',
    args: {
        'doctype': 'Address',
	    'filters': {'cep': cep},
        'fieldname': [
            'address_line1',
            'bairro',
            'city',
            'uf',
            'ibge',
            'address_line2'
        ]
    }, 
    callback: function(r) {
        // code snippet
    } 
    }); 
});

/*
frappe.ui.form.on("Address", "cep", function (frm) { 
    if (!frm.doc.cep) 
    return; 
frappe.call({ 
    method: 'ordem_servico.api.get_cep',
    args: {
        'doctype': 'Address',
	    'filters': {'cep': cep},
        'fieldname': [
            'address_line1',
            'bairro',
            'city',
            'uf',
            'ibge',
            'address_line2'
        ]
    }, 
    callback: function(r) {
        // code snippet
    } 
    }); 
});
*/