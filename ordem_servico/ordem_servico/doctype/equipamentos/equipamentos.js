// Copyright (c) 2024, laugusto and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipamentos', {
    refresh(frm) {
        frm.fields_dict.contact_link.get_query = function(doc) {
            return {
                query: "frappe.contacts.doctype.contact.contact.contact_query",
                filters: {
                    link_doctype: "Customer",
                    link_name: doc.customer
                }
            };
        };
    }
});
