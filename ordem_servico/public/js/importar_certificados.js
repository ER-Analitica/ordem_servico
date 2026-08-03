// Importação de certificados por pasta, para OS Interna e Externa.
// Casa o arquivo à OS pelo número no início do nome do arquivo (ex: 047632 -> OS-47632).

async function _importar_certificados(doctype, folder) {
    frappe.confirm(
        `Deseja importar para as <b>${doctype}</b> os Certificados enviados <b>Hoje</b> para a pasta ${folder}?`,
        async () => {
            frappe.show_alert({ message: '🔍 Buscando arquivos criados hoje...', indicator: 'blue' });

            const hoje = frappe.datetime.now_date();
            const inicio_dia = `${hoje} 00:00:00`;
            const fim_dia = `${hoje} 23:59:59`;

            let arquivos_resp = await frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'File',
                    filters: [
                        ['folder', '=', folder],
                        ['creation', '>=', inicio_dia],
                        ['creation', '<=', fim_dia]
                    ],
                    fields: ['file_name', 'file_url', 'creation'],
                    limit: 500
                }
            });

            let arquivos = arquivos_resp.message || [];
            if (arquivos.length === 0) {
                frappe.msgprint(`⚠️ Nenhum arquivo criado hoje na pasta ${folder}.`);
                return;
            }

            frappe.show_alert({ message: `📂 ${arquivos.length} arquivos encontrados hoje. Processando...`, indicator: 'blue' });

            for (let file of arquivos) {
                let match = file.file_name.match(/^0*(\d{3,6})/);
                if (!match) continue;
                let numero_os = match[1];
                let nome_os = `OS-${numero_os}`;

                let os_resp = await frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: doctype,
                        filters: { name: nome_os },
                        fields: ['name'],
                        limit: 1
                    }
                });

                if (!os_resp.message || os_resp.message.length === 0) {
                    frappe.show_alert({ message: `⚠️ Nenhuma OS encontrada para ${file.file_name}`, indicator: 'orange' });
                    continue;
                }

                let os_name = os_resp.message[0].name;

                // Anexa direto no banco, sem rodar o validate() da OS —
                // necessário para OS antigas sem os campos exigidos pelas validações.
                let anexo_resp = await frappe.call({
                    method: 'ordem_servico.doc_events.importar_certificados.anexar_certificado_forcado',
                    args: { doctype: doctype, name: os_name, file_url: file.file_url }
                });

                if (anexo_resp.message.ja_anexado) {
                    frappe.show_alert({ message: `⚠️ ${file.file_name} já estava anexado à ${os_name}`, indicator: 'orange' });
                } else {
                    frappe.show_alert({
                        message: `✅ Certificado vinculado à ${os_name}<br><a href="${file.file_url}" target="_blank">${file.file_name}</a>`,
                        indicator: 'green'
                    });
                }
            }

            frappe.msgprint('✅ Importação concluída: certificados de hoje vinculados com sucesso.');
        },
        () => {} // cancelado
    );
}

// Marca visualmente, na lista, as OS com pendência de rastreabilidade.
function _indicador_rastreabilidade(doc) {
    if (doc.rastreabilidade_alerta) {
        return [__('Padrão pendente'), 'orange', 'rastreabilidade_alerta,=,1'];
    }
}

// Reprocessa a rastreabilidade de várias OS de uma vez.
function _revincular_lote(listview, doctype) {
    var selecionadas = (listview.get_checked_items() || []).map(function (d) { return d.name; });

    var opcoes = [
        { label: `Somente as ${selecionadas.length} selecionadas`, value: 'selecionadas' },
        { label: 'Todas com alerta de rastreabilidade', value: 'pendentes' },
        { label: 'Todas com certificado e sem a tabela preenchida', value: 'sem_tabela' }
    ];
    if (!selecionadas.length) opcoes.shift();

    frappe.prompt(
        [{
            fieldname: 'escopo',
            fieldtype: 'Select',
            label: 'Reprocessar',
            options: opcoes.map(function (o) { return o.label; }).join('\n'),
            default: opcoes[0].label,
            reqd: 1
        }],
        function (values) {
            var escopo = (opcoes.find(function (o) { return o.label === values.escopo; }) || opcoes[0]).value;
            frappe.call({
                method: 'ordem_servico.doc_events.rastreabilidade_padroes.revincular_em_lote',
                args: { doctype: doctype, nomes: selecionadas, escopo: escopo },
                freeze: true,
                freeze_message: 'Reprocessando rastreabilidade...',
                callback: function (r) {
                    var res = r.message || {};
                    var msg = `<b>${res.processadas}</b> de <b>${res.total}</b> OS reprocessada(s).`;
                    if (res.com_alerta) {
                        msg += `<br>⚠️ <b>${res.com_alerta}</b> ainda com pendência de padrão.`;
                    }
                    if ((res.erros || []).length) {
                        msg += '<br><br><b>Não processadas:</b><br>' +
                            res.erros.map(function (e) { return `• ${e.os} — ${e.motivo}`; }).join('<br>');
                    }
                    frappe.msgprint({
                        title: 'Revincular padrões em lote',
                        indicator: res.com_alerta ? 'orange' : 'green',
                        message: msg
                    });
                    listview.refresh();
                }
            });
        },
        'Revincular padrões',
        'Reprocessar'
    );
}

function _config_lista_os(doctype, pasta) {
    return {
        add_fields: ['rastreabilidade_alerta'],
        get_indicator: _indicador_rastreabilidade,
        onload: function (listview) {
            listview.page.add_inner_button('Importar Certificados (Hoje)', function () {
                _importar_certificados(doctype, pasta);
            });
            listview.page.add_inner_button('Revincular padrões', function () {
                _revincular_lote(listview, doctype);
            });
        }
    };
}

frappe.listview_settings['Ordem Servico Externa'] =
    _config_lista_os('Ordem Servico Externa', 'Home/Ordem Servico Externa');

frappe.listview_settings['Ordem Servico Interna'] =
    _config_lista_os('Ordem Servico Interna', 'Home/Ordem Servico Interna');
