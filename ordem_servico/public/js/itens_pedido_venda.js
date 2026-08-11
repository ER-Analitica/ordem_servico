// Preenche a tabela de itens a partir do Pedido de Venda.
//
// Antes os itens vinham do Orçamento (via Client Script no banco). Como o
// orçamento aprovado vira Pedido de Venda, é o pedido que reflete o que foi
// efetivamente vendido — por isso a origem passou a ser ele.
//
// Vale para Ordem Servico Interna e Criador de Ordens de Servico em Lote,
// que usam o mesmo campo `os_items`.

function _preencher_itens_do_pedido(frm, campo_pedido) {
    var pedido = frm.doc[campo_pedido];

    if (!pedido) {
        frm.clear_table('os_items');
        frm.refresh_field('os_items');
        return;
    }

    frappe.call({
        method: 'frappe.client.get',
        args: { doctype: 'Sales Order', name: pedido },
        callback: function (r) {
            var pedido_doc = r.message;
            if (!pedido_doc) return;

            frm.clear_table('os_items');

            (pedido_doc.items || []).forEach(function (item) {
                var row = frm.add_child('os_items');
                row.item_code = item.item_code;
                row.item_name = item.item_name;
                row.item_qty = item.qty;
            });

            frm.refresh_field('os_items');
        }
    });
}

// O rótulo da tabela acompanha a origem dos itens: os registros novos vêm do
// Pedido de Venda, os antigos vieram do Orçamento. É só exibição — o campo e
// os dados continuam os mesmos, então formatos de impressão e a geração de
// orçamento seguem funcionando sem alteração.
function _ajustar_rotulo_itens(frm, campo_orcamento) {
    if (!frm.fields_dict || !frm.fields_dict.os_items) return;

    var rotulo = 'Itens para Orçamento';
    if (frm.doc.has_sales_order_link) {
        rotulo = 'Itens do Pedido';
    } else if (frm.doc[campo_orcamento]) {
        rotulo = 'Itens do Orçamento';
    }
    frm.set_df_property('os_items', 'label', rotulo);
}

frappe.ui.form.on('Ordem Servico Interna', {
    refresh: function (frm) {
        _ajustar_rotulo_itens(frm, 'has_quotation_link');
    },
    has_sales_order_link: function (frm) {
        _preencher_itens_do_pedido(frm, 'has_sales_order_link');
        _ajustar_rotulo_itens(frm, 'has_quotation_link');
    },
    possui_pedido_venda: function (frm) {
        // Desmarcou: limpa o vínculo e a tabela
        if (!frm.doc.possui_pedido_venda && frm.doc.has_sales_order_link) {
            frm.set_value('has_sales_order_link', '');
        }
        _ajustar_rotulo_itens(frm, 'has_quotation_link');
    }
});

frappe.ui.form.on('Criador de Ordens de Servico em Lote', {
    refresh: function (frm) {
        _ajustar_rotulo_itens(frm, 'orcamento');
    },
    has_sales_order_link: function (frm) {
        _preencher_itens_do_pedido(frm, 'has_sales_order_link');
        _ajustar_rotulo_itens(frm, 'orcamento');
    },
    possui_pedido_venda: function (frm) {
        if (!frm.doc.possui_pedido_venda && frm.doc.has_sales_order_link) {
            frm.set_value('has_sales_order_link', '');
        }
        _ajustar_rotulo_itens(frm, 'orcamento');
    }
});
