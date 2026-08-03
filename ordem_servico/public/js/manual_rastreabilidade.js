// Manual da rastreabilidade dos padrões + aviso de novidade.
//
// - ordem_servico.manual.abrir()  -> manual completo (botão nas listas)
// - Aviso de novidade: aparece uma vez por login, até a data limite abaixo.

frappe.provide('ordem_servico.manual');

// Data da atualização, exibida no aviso (formato dd/mm/aaaa)
ordem_servico.manual.DATA_ATUALIZACAO = '03/08/2026';

// Até quando o aviso de novidade aparece. Depois desta data ele para sozinho.
// Formato: aaaa-mm-dd
ordem_servico.manual.AVISO_ATE = '2026-08-07';

// ---------------------------------------------------------------- MANUAL ----

ordem_servico.manual.conteudo = function () {
    var sec = 'margin:22px 0 8px;padding-bottom:5px;border-bottom:2px solid #e9ecef;font-size:15px;';
    var sub = 'margin:16px 0 6px;font-size:13px;font-weight:600;';
    var box = 'background:#f8f9fa;border-left:3px solid #adb5bd;padding:9px 12px;margin:10px 0;font-size:12px;border-radius:0 4px 4px 0;';
    var aviso = 'background:#fff3cd;border-left:3px solid #ffc107;padding:9px 12px;margin:10px 0;font-size:12px;border-radius:0 4px 4px 0;';
    var pre = 'background:#f1f3f5;padding:8px 10px;border-radius:4px;font-size:12px;margin:6px 0;white-space:pre-wrap;';
    var tab = 'width:100%;font-size:12px;margin:10px 0;border-collapse:collapse;';
    var th = 'style="background:#f1f3f5;padding:6px 8px;border:1px solid #dee2e6;text-align:left;"';
    var td = 'style="padding:6px 8px;border:1px solid #dee2e6;vertical-align:top;"';

    return `
<div style="font-size:13px;line-height:1.6;">

  <div style="${box}">
    <b>O que é:</b> todo certificado de calibração tem uma seção
    <b>"Rastreabilidade dos Padrões"</b>, listando os padrões usados naquela
    calibração. Agora o sistema lê essa seção sozinho e monta a mesma tabela
    dentro da Ordem de Serviço — pronta para auditoria, sem digitar nada.
  </div>

  <h4 style="${sec}">Parte 1 — Cadastrar os padrões</h4>
  <p style="color:#6c757d;font-size:12px;margin:0 0 8px;">Feito 1 ou 2 vezes por ano.
  É a base de tudo: o sistema só reconhece no certificado o que está cadastrado.</p>

  <div style="${sub}">1.1 Nomear os arquivos</div>
  <p>Cada PDF precisa seguir este formato:</p>
  <div style="${pre}"><b>Código - Descrição - Val. dd-mm-aaaa.pdf</b></div>
  <p>Exemplos:</p>
  <div style="${pre}">H001A03FD - Filtro de Óxido de Holmio - Val. 03-11-2027.pdf
26605.01 - Padrão de Formazina 800 NTU - Val. 30-11-2025.pdf
MRC1 - F1000 - MRC de Fluoreto - Val. 30-08-2024.pdf</div>
  <div style="${aviso}">
    ⚠️ A data precisa ser <b>completa</b> — dia, mês e ano.
    Só o ano (<b>Val. 2027</b>) não serve.
  </div>

  <div style="${sub}">1.2 Subir para a pasta</div>
  <p>Coloque os PDFs em <b>Home/Padrões/&lt;ano&gt;</b> (exemplo: <b>Home/Padrões/2026</b>).
  O ano é para a sua organização — o sistema usa a pasta só para saber o que importar.</p>

  <div style="${sub}">1.3 Importar</div>
  <p>Lista <b>Padrao de Calibracao</b> → botão <b>"Importar Padrões"</b> → confirmar o ano.</p>
  <table style="${tab}">
    <tr><th ${th}>Resultado</th><th ${th}>O que significa</th></tr>
    <tr><td ${td}><b>Cadastrado(s)</b></td><td ${td}>Entraram sozinhos</td></tr>
    <tr><td ${td}><b>Já existente(s)</b></td><td ${td}>Já estavam no sistema — ignorados, não duplica</td></tr>
    <tr><td ${td}><b>A conferir</b></td><td ${td}>Precisam da sua confirmação</td></tr>
    <tr><td ${td}><b>Com problema</b></td><td ${td}>Nome fora do padrão — o motivo aparece na tela</td></tr>
  </table>

  <div style="${sub}">1.4 Os "a conferir" — por que existem</div>
  <p>Códigos nos formatos já conhecidos (<b>H001A03FD</b>, <b>26605.01</b>) entram sozinhos.
  Formatos diferentes (<b>MRC1 - F1000</b>, <b>MR3</b>) o sistema <b>não arrisca adivinhar</b>:
  o código é a chave que liga o padrão ao certificado — se ele for cadastrado errado,
  o vínculo fica errado depois.</p>
  <p>Esses aparecem com os campos já preenchidos para você conferir. Ajuste o que precisar
  e clique em <b>"Corrigir e importar"</b>, ou em <b>"Cadastrar todos os conferidos"</b> no rodapé.</p>
  <div style="${box}">
    💡 Pode rodar a importação quantas vezes quiser — o que já existe é ignorado.
  </div>

  <h4 style="${sec}">Parte 2 — O dia a dia: importar certificados</h4>

  <div style="${sub}">2.1 Subir os certificados</div>
  <p>Coloque os PDFs em <b>Home/Ordem Servico Externa</b> ou <b>Home/Ordem Servico Interna</b>.
  O nome do arquivo precisa <b>começar com o número da OS</b> —
  <b>021962</b>_01 - Cliente.pdf vai para a <b>OS-21962</b>.</p>

  <div style="${sub}">2.2 Importar</div>
  <p>Na lista da OS → <b>"Importar Certificados (Hoje)"</b>. O sistema anexa o certificado
  <b>e já lê os padrões automaticamente</b> — você não precisa fazer mais nada.</p>
  <div style="${aviso}">
    ⚠️ O botão só enxerga arquivos enviados <b>no mesmo dia</b>. Para certificados de
    dias anteriores, use o botão <b>"Revincular padrões"</b>.
  </div>

  <h4 style="${sec}">Parte 3 — Quando aparece pendência</h4>

  <div style="${sub}">3.1 A coluna "Situação"</div>
  <table style="${tab}">
    <tr><th ${th}>Status</th><th ${th}>Significa</th><th ${th}>O que fazer</th></tr>
    <tr><td ${td}>✅ <b>Vinculado</b></td><td ${td}>Padrão encontrado e ligado</td><td ${td}>Nada</td></tr>
    <tr><td ${td}>⚠️ <b>Não cadastrado</b></td><td ${td}>Esse padrão ainda não existe no sistema</td><td ${td}>Cadastrar (item 3.2)</td></tr>
    <tr><td ${td}>⚠️ <b>Validade divergente</b></td><td ${td}>O código existe, mas com outra validade — é outro documento</td><td ${td}>Cadastrar a versão correta</td></tr>
    <tr><td ${td}>⚠️ <b>Validade não lida</b></td><td ${td}>Não deu para ler a data no certificado</td><td ${td}>Conferir o PDF</td></tr>
    <tr><td ${td}>⚠️ <b>Validade não cobre a data</b></td><td ${td}>O padrão estava vencido na data da calibração</td><td ${td}><b>Avisar o responsável</b> — é problema de metrologia</td></tr>
  </table>

  <div style="${sub}">3.2 Botão "Cadastrar padrões pendentes"</div>
  <p>Fica no topo da OS. Abre um padrão por vez, <b>já com o código e a validade preenchidos</b>
  (lidos do certificado). Você só anexa o PDF do padrão e clica em <b>"Cadastrar e vincular"</b>.
  O sistema cadastra, refaz o vínculo na hora e passa para o próximo.</p>

  <div style="${sub}">3.3 Botão "Revincular padrões"</div>
  <p>Use quando cadastrou o padrão que faltava, ou quando o certificado é de um dia anterior.</p>
  <ul style="margin:6px 0 0 18px;padding:0;">
    <li><b>Dentro da OS:</b> refaz só aquela</li>
    <li><b>Na lista:</b> três opções — só as selecionadas, todas com alerta, ou
        <b>todas com certificado e sem a tabela preenchida</b> (esta serve para popular o histórico)</li>
  </ul>

  <h4 style="${sec}">Parte 4 — Acompanhamento</h4>
  <ul style="margin:6px 0 0 18px;padding:0;">
    <li><b>Faixa laranja no topo:</b> mostra quantas OS têm pendência; o link leva à lista já filtrada</li>
    <li><b>Tag "Padrão pendente":</b> marca as OS pendentes na listagem</li>
  </ul>

  <div style="${sub}">Padrões vencendo</div>
  <p>Na lista de padrões, cada um tem uma tag: 🟢 <b>Vigente</b> (mais de 60 dias),
  🟠 <b>Vence em Nd</b> (próximos 60 dias), 🔴 <b>Vencido</b>.</p>
  <p>O botão <b>"Padrões vencendo"</b> lista o que precisa de ação — e ignora os que
  já foram recalibrados, mostrando só o que realmente está pendente.</p>

  <h4 style="${sec}">Situações comuns</h4>
  <table style="${tab}">
    <tr><th ${th}>Situação</th><th ${th}>Causa e solução</th></tr>
    <tr><td ${td}>Importei o certificado e a tabela ficou vazia</td>
        <td ${td}>O PDF não tem texto — foi digitalizado em vez de gerado do Excel. Peça o arquivo original.</td></tr>
    <tr><td ${td}>Um padrão que existe aparece como "Não cadastrado"</td>
        <td ${td}>O código no certificado está diferente do cadastrado. Confira letra por letra, inclusive sufixos <b>- T</b> e <b>- H</b>.</td></tr>
    <tr><td ${td}>O mesmo padrão aparece duas vezes na tabela</td>
        <td ${td}>Normal em termo-higrômetro: <b>- T</b> e <b>- H</b> são dois canais do mesmo instrumento. A tabela espelha o certificado.</td></tr>
    <tr><td ${td}>Rodei a importação e não veio nada</td>
        <td ${td}>Ela só pega arquivos do dia. Para os antigos, use "Revincular padrões".</td></tr>
  </table>

  <h4 style="${sec}">Regras de ouro</h4>
  <ol style="margin:6px 0 0 18px;padding:0;">
    <li><b>Código certo no cadastro</b> — é a chave de tudo</li>
    <li><b>Nome do arquivo no formato</b> Código - Descrição - Val. dd-mm-aaaa</li>
    <li><b>Nunca apagar padrão antigo</b> — o histórico das calibrações depende dele</li>
    <li><b>Pendência não é opcional</b> — é justamente o que a auditoria olha</li>
  </ol>

</div>`;
};

ordem_servico.manual.abrir = function () {
    var d = new frappe.ui.Dialog({
        title: 'Manual — Rastreabilidade dos Padrões',
        size: 'large',
        fields: [{ fieldtype: 'HTML', options: ordem_servico.manual.conteudo() }],
        primary_action_label: 'Fechar',
        primary_action: function () { d.hide(); }
    });
    d.show();
};

// ------------------------------------------------- AVISO DE NOVIDADE --------

ordem_servico.manual.aviso_no_prazo = function () {
    try {
        var hoje = frappe.datetime.get_today();
        return hoje <= ordem_servico.manual.AVISO_ATE;
    } catch (e) {
        return false;
    }
};

ordem_servico.manual.mostrar_aviso = function (forcar) {
    try {
        if (!frappe.session || frappe.session.user === 'Guest') return;
        if (!forcar && !ordem_servico.manual.aviso_no_prazo()) return;

        // sessionStorage: aparece uma vez por login, não a cada F5
        var chave = 'os_aviso_rastreabilidade_' + (frappe.session.user || '');
        if (!forcar && sessionStorage.getItem(chave)) return;
        try { sessionStorage.setItem(chave, '1'); } catch (e) {}

        var d = new frappe.ui.Dialog({
            title: '📢 Novidade: Rastreabilidade dos Padrões',
            size: 'large',
            fields: [{
                fieldtype: 'HTML',
                options: `
<div style="font-size:13px;line-height:1.7;">
  <div style="color:#868e96;font-size:11px;letter-spacing:.4px;text-transform:uppercase;
              margin:-4px 0 12px;padding-bottom:8px;border-bottom:1px solid #e9ecef;">
    Atualização de ${ordem_servico.manual.DATA_ATUALIZACAO}
  </div>

  <p>Foram implementadas as seguintes funcionalidades:</p>

  <div style="margin:14px 0;">
    <div style="margin-bottom:12px;">
      <b>📋 Cadastro de Padrões de Calibração</b><br>
      <span style="color:#495057;">Novo cadastro para os padrões usados nas calibrações,
      com importação em massa a partir da pasta de arquivos.</span>
    </div>

    <div style="margin-bottom:12px;">
      <b>📄 Leitura automática do certificado</b><br>
      <span style="color:#495057;">Ao anexar o certificado na OS, o sistema lê os padrões
      listados no PDF e preenche sozinho a nova tabela
      <b>"Rastreabilidade dos Padrões"</b>, ligando cada um ao seu cadastro.</span>
    </div>

    <div style="margin-bottom:12px;">
      <b>⚠️ Sinalização de pendências</b><br>
      <span style="color:#495057;">Quando algum padrão não é localizado, a OS fica
      marcada e um botão na própria tela permite cadastrar e vincular na hora.</span>
    </div>

    <div style="margin-bottom:12px;">
      <b>📅 Controle de validade dos padrões</b><br>
      <span style="color:#495057;">Relatório de padrões vencidos e a vencer nos
      próximos 60 dias, com indicação visual na listagem.</span>
    </div>
  </div>

  <p style="margin-top:16px;color:#6c757d;">O passo a passo de cada uma está no botão
  <b>Manual</b>, em <b>Padrao de Calibracao</b>.</p>
</div>`
            }],
            primary_action_label: 'Entendi',
            primary_action: function () { d.hide(); }
        });
        d.show();
    } catch (e) {
        console.warn('Aviso de novidade: falha ao exibir', e);
    }
};

$(document).on('app_ready', function () {
    // Pequeno atraso para não competir com o carregamento do desk
    setTimeout(function () {
        ordem_servico.manual.mostrar_aviso(false);
    }, 1500);
});
