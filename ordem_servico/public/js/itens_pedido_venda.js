// Preenche a tabela de itens a partir do Pedido de Venda.
//
// Antes os itens vinham do Orçamento (via Client Script no banco). Como o
// orçamento aprovado vira Pedido de Venda, é o pedido que reflete o que foi
// efetivamente vendido — por isso a origem passou a ser ele.
//
// Vale para Ordem Servico Interna e Criador de Ordens de Servico em Lote,
// que usam o mesmo campo `os_items`.

// Um Text Editor "vazio" guarda sobras de marcação (`<p></p>`, `<p><br></p>`),
// não string vazia. Mesma checagem que o servidor faz em pontos_calibracao_os.
function _texto_vazio(html) {
    if (!html) return true;
    // \u00a0 e o espaco nao separavel em que o &nbsp; se transforma no texto
    var texto = $('<div>').html(html).text().replace(/\u00a0/g, ' ');
    return !texto.trim();
}

// Os Pontos de Calibração acompanham os itens: quem escolhe o pedido espera ver
// tudo que vem dele na hora, sem precisar salvar.
//
// Aqui o valor é substituído, não completado. Estas funções só rodam quando a
// pessoa troca o pedido no formulário, e nesse momento o que estava no campo
// era do pedido anterior — mesma lógica dos itens, que são limpos e recarregados.
// Se o pedido novo não tiver pontos, o campo fica em branco.
//
// A proteção do ajuste do técnico está no servidor: num save comum o campo só é
// preenchido se estiver vazio, então nada do que ele escrever se perde depois.
function _aplicar_pontos_do_pedido(frm, pontos) {
    if (!frm.fields_dict || !frm.fields_dict.pontos_cal_criterios_aceitacao) return;

    var novo = _texto_vazio(pontos) ? '' : pontos;
    if (novo === frm.doc.pontos_cal_criterios_aceitacao) return;

    frm.set_value('pontos_cal_criterios_aceitacao', novo);
}

// Busca o pedido só para os pontos — usado onde não há tabela de itens.
function _buscar_pontos_do_pedido(frm, campo_pedido) {
    var pedido = frm.doc[campo_pedido];

    if (!pedido) {
        _aplicar_pontos_do_pedido(frm, '');
        return;
    }

    frappe.db.get_value('Sales Order', pedido, 'pontos_de_calibracao')
        .then(function (r) {
            _aplicar_pontos_do_pedido(frm, (r && r.message) ? r.message.pontos_de_calibracao : '');
        });
}

function _preencher_itens_do_pedido(frm, campo_pedido) {
    var pedido = frm.doc[campo_pedido];

    if (!pedido) {
        frm.clear_table('os_items');
        frm.refresh_field('os_items');
        _aplicar_pontos_do_pedido(frm, '');
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
            _aplicar_pontos_do_pedido(frm, pedido_doc.pontos_de_calibracao);
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

// A OS Externa não tem tabela de itens, mas tem o mesmo campo de pontos e o
// vínculo com o pedido em outro campo.
frappe.ui.form.on('Ordem Servico Externa', {
    sales_order_reference: function (frm) {
        _buscar_pontos_do_pedido(frm, 'sales_order_reference');
    }
});
