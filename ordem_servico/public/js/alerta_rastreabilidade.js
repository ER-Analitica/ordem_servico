// Barra de aviso no topo do desk quando há OS com pendência de rastreabilidade.
// A contagem é viva: some sozinha quando as pendências são resolvidas.

frappe.provide('ordem_servico.rastreabilidade');

// Quem vê o aviso é decidido no servidor (USUARIOS_AVISO_RASTREABILIDADE, em
// rastreabilidade_padroes.py): para quem não está na lista a contagem volta
// zerada e a barra não é montada. Regra num lugar só, sem risco de divergir.

ordem_servico.rastreabilidade.mostrar_barra = function () {
    if (!frappe.session || frappe.session.user === 'Guest') return;

    frappe.call({
        method: 'ordem_servico.doc_events.rastreabilidade_padroes.contar_alertas',
        callback: function (r) {
            var res = r.message || {};
            var total = (res.interna || 0) + (res.externa || 0);
            var $barra = $('#os-rastreabilidade-barra');

            if (!total) {
                $barra.remove();
                return;
            }

            var partes = [];
            if (res.externa) partes.push(`<a href="/app/ordem-servico-externa?rastreabilidade_alerta=1" style="color:#7a4a00;text-decoration:underline;">${res.externa} OS Externa</a>`);
            if (res.interna) partes.push(`<a href="/app/ordem-servico-interna?rastreabilidade_alerta=1" style="color:#7a4a00;text-decoration:underline;">${res.interna} OS Interna</a>`);

            var html = `
                <div id="os-rastreabilidade-barra" style="
                    background:#fff3cd;border-bottom:1px solid #ffe08a;color:#7a4a00;
                    padding:8px 16px;font-size:13px;display:flex;
                    justify-content:space-between;align-items:center;">
                    <div>⚠️ <b>Rastreabilidade dos padrões pendente</b> —
                        ${partes.join(' e ')} com padrão faltando ou divergente. Verificar.</div>
                    <span style="cursor:pointer;font-size:16px;line-height:1;" title="Ocultar até o próximo login"
                          onclick="$('#os-rastreabilidade-barra').remove()">&times;</span>
                </div>`;

            if ($barra.length) {
                $barra.replaceWith(html);
            } else {
                $('.main-section, .body-sidebar-container').first().before(html);
            }
        }
    });
};

$(document).on('app_ready', function () {
    ordem_servico.rastreabilidade.mostrar_barra();
    // Reavalia ao trocar de rota, para a contagem acompanhar as correções
    frappe.router.on('change', function () {
        ordem_servico.rastreabilidade.mostrar_barra();
    });
});
