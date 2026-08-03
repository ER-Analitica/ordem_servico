// Importação em massa de Padrões de Calibração, com correção assistida
// dos arquivos cujo nome está fora do padrão.

frappe.listview_settings['Padrao de Calibracao'] = {
    add_fields: ['validade'],
    get_indicator: function (doc) {
        if (!doc.validade) return;
        var dias = frappe.datetime.get_day_diff(doc.validade, frappe.datetime.get_today());
        if (dias < 0) return [__('Vencido'), 'red', 'validade,<,Today'];
        if (dias <= 60) return [__('Vence em ' + dias + 'd'), 'orange', 'validade,<=,Today'];
        return [__('Vigente'), 'green', 'validade,>,Today'];
    },
    onload: function (listview) {
        listview.page.add_inner_button('Manual', function () {
            if (ordem_servico && ordem_servico.manual) {
                ordem_servico.manual.abrir();
            }
        });

        listview.page.add_inner_button('Padrões vencendo', function () {
            frappe.call({
                method: 'ordem_servico.ordem_servico.doctype.padrao_de_calibracao.padrao_de_calibracao.padroes_vencendo',
                args: { dias: 60 },
                freeze: true,
                callback: function (r) {
                    var lista = r.message || [];
                    if (!lista.length) {
                        frappe.msgprint({
                            title: 'Padrões vencendo',
                            indicator: 'green',
                            message: '✅ Nenhum padrão vencido ou vencendo nos próximos 60 dias.'
                        });
                        return;
                    }
                    var linhas = lista.map(function (p) {
                        var cor = p.situacao === 'Vencido' ? '#dc3545' : '#e67e22';
                        var quando = p.dias < 0 ? `vencido há ${Math.abs(p.dias)} dia(s)` : `vence em ${p.dias} dia(s)`;
                        return `<tr>
                            <td><a href="/app/padrao-de-calibracao/${encodeURIComponent(p.name)}">${p.codigo}</a></td>
                            <td>${frappe.utils.escape_html(p.descricao || '—')}</td>
                            <td>${frappe.datetime.str_to_user(p.validade)}</td>
                            <td style="color:${cor};font-weight:bold;">${quando}</td>
                        </tr>`;
                    }).join('');
                    frappe.msgprint({
                        title: `Padrões vencendo (${lista.length})`,
                        indicator: 'orange',
                        message: `<div style="overflow-x:auto;">
                            <table class="table table-bordered" style="font-size:12px;">
                            <thead><tr><th>Código</th><th>Descrição</th><th>Validade</th><th>Situação</th></tr></thead>
                            <tbody>${linhas}</tbody></table></div>
                            <div style="font-size:12px;color:#6c757d;">
                            Padrão vencido invalida a rastreabilidade das calibrações que o utilizarem.</div>`
                    });
                }
            });
        });

        listview.page.add_inner_button('Importar Padrões', function () {
            var ano_atual = new Date().getFullYear();
            frappe.prompt(
                [{
                    fieldname: 'ano',
                    fieldtype: 'Int',
                    label: 'Ano dos padrões em uso',
                    default: ano_atual,
                    reqd: 1,
                    description: 'Lê a pasta Home/Padrões/&lt;ano&gt;. Padrões já cadastrados são ignorados.'
                }],
                function (values) {
                    frappe.call({
                        method: 'ordem_servico.doc_events.importar_padroes.importar_padroes',
                        args: { ano: values.ano },
                        freeze: true,
                        freeze_message: 'Lendo a pasta de padrões...',
                        callback: function (r) {
                            _mostrar_resultado(r.message || {}, listview);
                        }
                    });
                },
                'Importar Padrões',
                'Importar'
            );
        });
    }
};

function _mostrar_resultado(res, listview) {
    var criados = res.criados || [];
    var ignorados = res.ignorados || [];
    var conferir = res.conferir || [];
    var falhas = (res.falhas || []).concat(conferir);

    if (!res.total) {
        frappe.msgprint({
            title: 'Importar Padrões',
            indicator: 'orange',
            message: 'Nenhum arquivo encontrado em <b>' + (res.pasta || '') + '</b>.<br>' +
                'Verifique se a pasta existe e contém os PDFs dos padrões.'
        });
        return;
    }

    var resumo = `
        <div style="margin-bottom:15px;">
            <div style="font-size:12px;color:#6c757d;margin-bottom:6px;">Pasta lida: <b>${res.pasta || ''}</b></div>
            <b>${res.total}</b> arquivo(s) na pasta &nbsp;|&nbsp;
            <span style="color:#28a745;"><b>${criados.length}</b> cadastrado(s)</span> &nbsp;|&nbsp;
            <span style="color:#6c757d;"><b>${ignorados.length}</b> já existente(s)</span> &nbsp;|&nbsp;
            <span style="color:#e67e22;"><b>${conferir.length}</b> a conferir</span> &nbsp;|&nbsp;
            <span style="color:#dc3545;"><b>${(res.falhas || []).length}</b> com problema</span>
        </div>`;

    if (!falhas.length) {
        frappe.msgprint({
            title: 'Importar Padrões',
            indicator: 'green',
            message: resumo + '✅ Todos os arquivos válidos foram importados.'
        });
        listview.refresh();
        return;
    }

    var linhas = falhas.map(function (f, i) {
        return `
        <div class="falha-row" data-i="${i}" style="border:1px solid #d1d8dd;border-radius:6px;padding:12px;margin-bottom:12px;">
            <div style="font-size:12px;color:#6c757d;">${frappe.utils.escape_html(f.folder || '')}</div>
            <div style="font-weight:bold;margin-bottom:4px;">${frappe.utils.escape_html(f.file_name)}</div>
            <div style="color:#dc3545;font-size:12px;margin-bottom:10px;">⚠️ ${f.motivo}</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end;">
                <div style="flex:1;min-width:120px;">
                    <label style="font-size:11px;">Código</label>
                    <input class="form-control input-sm f-codigo" value="${frappe.utils.escape_html(f.codigo || '')}" placeholder="H001A03FD">
                </div>
                <div style="flex:2;min-width:160px;">
                    <label style="font-size:11px;">Descrição</label>
                    <input class="form-control input-sm f-descricao" value="${frappe.utils.escape_html(f.descricao || '')}" placeholder="Filtro Óptico de Hólmio">
                </div>
                <div style="flex:1;min-width:130px;">
                    <label style="font-size:11px;">Validade</label>
                    <input type="date" class="form-control input-sm f-validade" value="${f.validade || ''}">
                </div>
                <button class="btn btn-sm btn-primary btn-corrigir" data-i="${i}">Corrigir e importar</button>
            </div>
            <div class="f-status" style="font-size:12px;margin-top:6px;"></div>
        </div>`;
    }).join('');

    var d = new frappe.ui.Dialog({
        title: 'Importar Padrões',
        size: 'large',
        fields: [{
            fieldname: 'corpo',
            fieldtype: 'HTML',
            options: resumo +
                '<div style="margin-bottom:10px;">Confira o <b>código</b> de cada item abaixo — ' +
                'é ele que liga o padrão ao certificado. Corrija o que precisar e cadastre.</div>' + linhas
        }],
        primary_action_label: 'Cadastrar todos os conferidos',
        primary_action: function () {
            var $pendentes = d.$wrapper.find('.btn-corrigir:not(:disabled)');
            if (!$pendentes.length) {
                frappe.show_alert('Nenhum item pendente.');
                return;
            }
            $pendentes.each(function (i) {
                var $b = $(this);
                setTimeout(function () { $b.trigger('click'); }, i * 350);
            });
        }
    });
    d.show();

    d.$wrapper.on('click', '.btn-corrigir', function () {
        var $btn = $(this);
        var $row = $btn.closest('.falha-row');
        var i = parseInt($btn.attr('data-i'), 10);
        var f = falhas[i];

        var codigo = $row.find('.f-codigo').val();
        var descricao = $row.find('.f-descricao').val();
        var validade = $row.find('.f-validade').val();
        var $status = $row.find('.f-status');

        if (!codigo || !validade) {
            $status.html('<span style="color:#dc3545;">Preencha código e validade.</span>');
            return;
        }

        frappe.call({
            method: 'ordem_servico.doc_events.importar_padroes.importar_corrigido',
            args: {
                codigo: codigo,
                descricao: descricao,
                validade: validade,
                file_url: f.file_url
            },
            callback: function (r) {
                var res = r.message || {};
                if (res.ok) {
                    $row.css({ opacity: 0.6, 'border-color': '#28a745' });
                    $btn.prop('disabled', true);
                    $status.html('<span style="color:#28a745;">✅ Cadastrado como ' + res.name +
                        ' — lembre de renomear o arquivo na pasta para o padrão.</span>');
                    listview.refresh();
                } else {
                    $status.html('<span style="color:#dc3545;">' + (res.motivo || 'Falhou.') + '</span>');
                }
            },
            error: function () {
                $status.html('<span style="color:#dc3545;">Erro ao cadastrar — verifique os dados.</span>');
            }
        });
    });
}
