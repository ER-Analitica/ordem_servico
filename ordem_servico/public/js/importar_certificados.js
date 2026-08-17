// Importação de certificados a partir da pasta única Home/Certificados.
//
// O arquivo casa com a OS pelo número no início do nome (ex: 047632 -> OS-47632),
// e o próprio número diz se a OS é Interna ou Externa — por isso o botão faz a
// mesma coisa nas duas listas, e a distribuição é automática.
//
// O reconhecimento (quais arquivos existem, de quem são, quais já estão
// anexados) sai numa chamada só. Depois o que sobrou é processado em fatias,
// de MAX_POR_LOTE por vez: é a fatia que dá o progresso ao lado, sem uma ida
// ao servidor por arquivo.

const MAX_POR_LOTE = 10;

// Acima deste tamanho, mostrar um aviso por certificado empilharia dezenas
// deles na tela ao mesmo tempo. A partir daí o acompanhamento passa a ser o
// contador de progresso — os certificados importados continuam todos no
// resumo final, e as falhas continuam avisando uma a uma.
const MAX_AVISOS_INDIVIDUAIS = 50;

async function _importar_certificados() {
    const reconhecimento = await frappe.call({
        method: 'ordem_servico.doc_events.importar_certificados.listar_pendentes',
        freeze: true,
        freeze_message: 'Lendo a pasta de certificados...'
    });

    const dados = (reconhecimento && reconhecimento.message) || {};
    const pendentes = dados.pendentes || [];

    if (!pendentes.length) {
        frappe.msgprint({
            title: 'Importar certificados',
            indicator: 'blue',
            message: _resumo_sem_pendentes(dados)
        });
        return;
    }

    frappe.confirm(
        `Foram encontrados <b>${pendentes.length}</b> certificado(s) novo(s) na pasta ` +
        `<b>Certificados</b>.<br>Deseja importar agora?`,
        async () => {
            const importados = [];
            const falhas = [];
            let ja_anexados = dados.ja_anexados || 0;
            const avisar_um_a_um = pendentes.length <= MAX_AVISOS_INDIVIDUAIS;

            for (let inicio = 0; inicio < pendentes.length; inicio += MAX_POR_LOTE) {
                const fatia = pendentes.slice(inicio, inicio + MAX_POR_LOTE);

                let resultados = null;
                try {
                    const resposta = await frappe.call({
                        method: 'ordem_servico.doc_events.importar_certificados.processar_lote',
                        args: { itens: JSON.stringify(fatia) }
                    });
                    resultados = resposta && resposta.message;
                } catch (e) {
                    resultados = null;
                }

                if (!resultados) {
                    // A fatia não chegou ao servidor, ou voltou sem resposta.
                    // Entra inteira no resumo como não importada — o que já foi
                    // importado nas fatias anteriores continua valendo.
                    fatia.forEach(function (item) {
                        falhas.push({ file_name: item.file_name, motivo: 'sem resposta do servidor' });
                    });
                    continue;
                }

                resultados.forEach(function (r) {
                    if (!r.ok) {
                        falhas.push({ file_name: r.file_name, motivo: r.motivo });
                        frappe.show_alert({
                            message: `❌ ${r.file_name} não foi importado`,
                            indicator: 'red'
                        }, 5);
                    } else if (r.ja_anexado) {
                        ja_anexados += 1;
                    } else {
                        importados.push(r);
                        if (avisar_um_a_um) {
                            frappe.show_alert({
                                message: `✅ ${r.os_name}<br>` +
                                    `<a href="${r.file_url}" target="_blank">${r.file_name}</a>`,
                                indicator: 'green'
                            }, 5);
                        }
                    }
                });

                if (!avisar_um_a_um) {
                    const feitos = Math.min(inicio + MAX_POR_LOTE, pendentes.length);
                    frappe.show_alert({
                        message: `📄 ${feitos} de ${pendentes.length} certificados processados...`,
                        indicator: 'blue'
                    }, 3);
                }
            }

            frappe.msgprint({
                title: 'Importação concluída',
                indicator: falhas.length ? 'orange' : 'green',
                message: _resumo_final(importados, ja_anexados, falhas, dados)
            });
        },
        () => {} // cancelado
    );
}

// Lista de nomes de arquivo, cortada para o aviso não virar uma parede.
function _lista_arquivos(nomes) {
    const mostrados = nomes.slice(0, 20).map(function (n) { return `• ${n}`; }).join('<br>');
    const resto = nomes.length - 20;
    return resto > 0 ? `${mostrados}<br>• ... e mais ${resto}` : mostrados;
}

function _pendencias_da_pasta(dados) {
    const blocos = [];

    if ((dados.sem_os || []).length) {
        blocos.push(`<b>Sem OS correspondente (${dados.sem_os.length}):</b><br>` +
            _lista_arquivos(dados.sem_os));
    }
    if ((dados.sem_numero || []).length) {
        blocos.push(`<b>Sem número de OS no nome (${dados.sem_numero.length}):</b><br>` +
            _lista_arquivos(dados.sem_numero));
    }
    if ((dados.ambiguos || []).length) {
        blocos.push(`<b>Número existe na Interna e na Externa (${dados.ambiguos.length}):</b><br>` +
            _lista_arquivos(dados.ambiguos));
    }

    return blocos;
}

function _resumo_sem_pendentes(dados) {
    if (!dados.total_na_pasta) {
        return 'A pasta <b>Certificados</b> está vazia.';
    }

    const partes = ['Nenhum certificado novo para importar.'];
    if (dados.ja_anexados) {
        partes.push(`<b>${dados.ja_anexados}</b> já estava(m) anexado(s) à sua OS.`);
    }

    return partes.concat(_pendencias_da_pasta(dados)).join('<br><br>');
}

function _resumo_final(importados, ja_anexados, falhas, dados) {
    const partes = [`✅ <b>${importados.length}</b> certificado(s) importado(s).`];

    if (ja_anexados) {
        partes.push(`<b>${ja_anexados}</b> já estava(m) anexado(s) e foram ignorados.`);
    }
    if (falhas.length) {
        partes.push(`<b>Não importados (${falhas.length}):</b><br>` +
            falhas.slice(0, 20).map(function (f) {
                return `• ${f.file_name} — ${f.motivo}`;
            }).join('<br>') +
            (falhas.length > 20 ? `<br>• ... e mais ${falhas.length - 20}` : ''));
    }

    return partes.concat(_pendencias_da_pasta(dados)).join('<br><br>');
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

// O botão faz a mesma coisa nas duas listas: a pasta é única e a separação
// entre Interna e Externa é feita pelo número da OS, no servidor.
function _config_lista_os(doctype) {
    return {
        add_fields: ['rastreabilidade_alerta'],
        get_indicator: _indicador_rastreabilidade,
        onload: function (listview) {
            listview.page.add_inner_button('Importar Certificados', function () {
                _importar_certificados();
            });
            listview.page.add_inner_button('Revincular padrões', function () {
                _revincular_lote(listview, doctype);
            });
        }
    };
}

frappe.listview_settings['Ordem Servico Externa'] = _config_lista_os('Ordem Servico Externa');

frappe.listview_settings['Ordem Servico Interna'] = _config_lista_os('Ordem Servico Interna');
