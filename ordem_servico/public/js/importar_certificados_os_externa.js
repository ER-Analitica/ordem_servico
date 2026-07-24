frappe.listview_settings['Ordem Servico Externa'] = {
    onload: function(listview) {
        listview.page.add_inner_button('Importar Certificados (Hoje)', async function() {
            frappe.confirm(
                `Deseja importar para as Ordens de Serviço Externa os Certificados enviados <b>Hoje</b> para a pasta Home/Ordem Servico Externa?`,
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
                                ['folder', '=', 'Home/Ordem Servico Externa'],
                                ['creation', '>=', inicio_dia],
                                ['creation', '<=', fim_dia]
                            ],
                            fields: ['file_name', 'file_url', 'creation'],
                            limit: 500
                        }
                    });

                    let arquivos = arquivos_resp.message || [];
                    if (arquivos.length === 0) {
                        frappe.msgprint('⚠️ Nenhum arquivo criado hoje na pasta Home/Ordem Servico Externa.');
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
                                doctype: 'Ordem Servico Externa',
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
                        // necessário para OS antigas sem os campos exigidos pelas
                        // validações criadas depois (data de calibração, equipamento).
                        let anexo_resp = await frappe.call({
                            method: 'ordem_servico.doc_events.importar_certificados.anexar_certificado_forcado',
                            args: { name: os_name, file_url: file.file_url }
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
        });
    }
};
