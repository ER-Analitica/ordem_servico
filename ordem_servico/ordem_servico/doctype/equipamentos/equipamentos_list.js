// Auditoria de duplicidade com mesclagem na própria tela.
frappe.listview_settings["Equipamentos"] = {
	onload(listview) {
		listview.page.add_inner_button("Auditoria de Duplicidade", () => {
			abrir_auditoria_duplicidade();
		});
	},
};

function abrir_auditoria_duplicidade() {
	frappe.call({
		method: "ordem_servico.doc_events.auditoria_duplicidade_equipamentos.grupos_de_duplicatas",
		freeze: true,
		freeze_message: "Analisando a base de equipamentos...",
		callback(r) {
			const grupos = r.message || [];
			if (!grupos.length) {
				frappe.msgprint({
					title: "Auditoria de Duplicidade",
					indicator: "green",
					message: "Nenhuma suspeita de duplicidade encontrada. Base limpa! ✅"
				});
				return;
			}
			renderizar_auditoria(grupos);
		}
	});
}

function renderizar_auditoria(grupos) {
	const cores = { A: "#c0392b", B: "#e67e22", C: "#2980b9" };

	const html = grupos.map((g, gi) => {
		const linhas = g.itens.map((item, ii) => `
			<tr>
				<td><input type="radio" name="grupo-${gi}" value="${item.name}" ${ii === 0 ? "checked" : ""}></td>
				<td><a href="/app/equipamentos/${encodeURIComponent(item.name)}" target="_blank">${item.name}</a></td>
				<td>${item.customer || "—"}</td>
				<td>${item.numero_serie || "—"}</td>
				<td>${item.tag || "—"}</td>
				<td>${item.descricao || "—"}</td>
				<td>${item.modelo_equipamento || "—"}</td>
				<td>${item.marca_equipamento || "—"}</td>
				<td style="text-align:center;"><b>${item.os_count}</b></td>
			</tr>`).join("");

		return `
			<div class="dup-grupo" data-gi="${gi}" style="margin-bottom:25px;border:1px solid #d1d8dd;border-radius:6px;padding:12px;">
				<div style="margin-bottom:8px;">
					<span style="color:${cores[g.tipo]};font-weight:bold;">[Grupo ${g.tipo}]</span>
					<b>${g.titulo}</b><br>
					<i class="text-muted">${g.confianca}</i>
				</div>
				<div style="overflow-x:auto;">
				<table class="table table-bordered" style="font-size:12px;margin-bottom:8px;">
					<thead><tr>
						<th>Manter</th><th>ID</th><th>Cliente</th><th>Série</th><th>Tag</th>
						<th>Equipamento</th><th>Modelo</th><th>Marca</th><th>OSs</th>
					</tr></thead>
					<tbody>${linhas}</tbody>
				</table>
				</div>
				<button class="btn btn-xs btn-danger btn-mesclar-grupo" data-gi="${gi}">
					Mesclar grupo no selecionado
				</button>
				<span class="text-muted" style="font-size:11px;margin-left:8px;">
					Os demais registros serão mesclados no marcado em "Manter" — as OS são reapontadas automaticamente.
				</span>
			</div>`;
	}).join("");

	const d = new frappe.ui.Dialog({
		title: `Auditoria de Duplicidade — ${grupos.length} grupo(s) suspeito(s)`,
		size: "extra-large",
		fields: [{ fieldname: "corpo", fieldtype: "HTML", options: html }]
	});
	d.show();

	d.$wrapper.on("click", ".btn-mesclar-grupo", function () {
		const gi = parseInt($(this).attr("data-gi"), 10);
		const grupo = grupos[gi];
		const sobrevivente = d.$wrapper.find(`input[name="grupo-${gi}"]:checked`).val();
		if (!sobrevivente) {
			frappe.msgprint("Selecione qual registro deve ser mantido.");
			return;
		}
		const origens = grupo.itens.map(i => i.name).filter(n => n !== sobrevivente);

		let aviso_extra = "";
		if (grupo.tipo === "C") {
			aviso_extra = "<br><br><b style='color:#c0392b;'>Atenção:</b> este grupo envolve " +
				"clientes diferentes — confirme com o comercial qual é o dono correto antes de mesclar.";
		}

		frappe.confirm(
			`Mesclar <b>${origens.length}</b> registro(s) (${origens.join(", ")}) ` +
			`dentro de <b>${sobrevivente}</b>?<br>` +
			`As OS vinculadas serão reapontadas e os registros de origem serão excluídos. ` +
			`Esta ação não pode ser desfeita.${aviso_extra}`,
			async () => {
				for (const origem of origens) {
					await frappe.call({
						method: "ordem_servico.doc_events.auditoria_duplicidade_equipamentos.mesclar_equipamentos",
						args: { origem: origem, destino: sobrevivente },
						freeze: true,
						freeze_message: `Mesclando ${origem} em ${sobrevivente}...`
					});
				}
				frappe.show_alert({ message: "Grupo mesclado com sucesso.", indicator: "green" });
				d.hide();
				abrir_auditoria_duplicidade(); // reabre com os dados atualizados
			}
		);
	});
}
