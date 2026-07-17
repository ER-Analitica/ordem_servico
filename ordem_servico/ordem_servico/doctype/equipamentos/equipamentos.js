// Copyright (c) 2024, laugusto and contributors
// For license information, please see license.txt

function verificar_duplicidade_equipamento(frm) {
    if (!frm.doc.customer) return;
    // Só consulta quando há informação suficiente para comparar
    if (!frm.doc.numero_serie && !frm.doc.tag && !frm.doc.descricao) return;

    frappe.call({
        method: "ordem_servico.doc_events.validacao_duplicidade_equipamentos.verificar_duplicidade",
        args: {
            customer: frm.doc.customer,
            numero_serie: frm.doc.numero_serie || "",
            tag: frm.doc.tag || "",
            descricao: frm.doc.descricao || "",
            modelo: frm.doc.modelo_equipamento || "",
            marca: frm.doc.marca_equipamento || "",
            ignorar: frm.doc.name
        },
        callback(r) {
            const matches = r.message || [];
            if (!matches.length) return;

            const tem_bloqueio = matches.some(m => m.nivel === "bloqueio");
            const linhas = matches.map(m => {
                const rotulo = m.nivel === "bloqueio"
                    ? '<span style="color:#c0392b;font-weight:bold;">DUPLICADO — o salvamento será bloqueado</span>'
                    : '<span style="color:#e67e22;font-weight:bold;">PARECIDO — verifique antes de salvar</span>';
                return `${rotulo}<br>
                    <a href="/app/equipamentos/${encodeURIComponent(m.name)}" target="_blank">${m.name}</a>
                    — ${m.descricao || "—"} | Modelo: ${m.modelo_equipamento || "—"}
                    | Marca: ${m.marca_equipamento || "—"} | Série: ${m.numero_serie || "—"}
                    | Tag: ${m.tag || "—"}<br><i>${m.motivo}</i>`;
            });

            frappe.msgprint({
                title: "Equipamento possivelmente já cadastrado",
                indicator: tem_bloqueio ? "red" : "orange",
                message: linhas.join("<br><br>")
            });
        }
    });
}

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
    },
    numero_serie(frm) {
        verificar_duplicidade_equipamento(frm);
    },
    tag(frm) {
        verificar_duplicidade_equipamento(frm);
    },
    customer(frm) {
        verificar_duplicidade_equipamento(frm);
    },
    descricao(frm) {
        verificar_duplicidade_equipamento(frm);
    },
    modelo_equipamento(frm) {
        verificar_duplicidade_equipamento(frm);
    },
    marca_equipamento(frm) {
        verificar_duplicidade_equipamento(frm);
    }
});
