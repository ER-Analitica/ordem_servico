// Alerta de duplicidade em tempo real no popup de criação rápida de Equipamentos.
// O Frappe procura frappe.ui.form.<DocTypeSemEspaços>QuickEntryForm ao abrir o popup.
$(document).ready(function () {
	if (!frappe.ui.form || !frappe.ui.form.QuickEntryForm) return;

	frappe.ui.form.EquipamentosQuickEntryForm = class EquipamentosQuickEntryForm extends (
		frappe.ui.form.QuickEntryForm
	) {
		render_dialog() {
			super.render_dialog();
			const dialog = this.dialog;

			const checar_duplicidade = () => {
				const v = dialog.get_values(true) || {};
				if (!v.customer) return;
				if (!v.numero_serie && !v.tag && !v.descricao) return;

				frappe.call({
					method: "ordem_servico.doc_events.validacao_duplicidade_equipamentos.verificar_duplicidade",
					args: {
						customer: v.customer,
						numero_serie: v.numero_serie || "",
						tag: v.tag || "",
						descricao: v.descricao || "",
						modelo: v.modelo_equipamento || "",
						marca: v.marca_equipamento || ""
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
			};

			["customer", "numero_serie", "tag", "descricao", "modelo_equipamento", "marca_equipamento"].forEach(fieldname => {
				const field = dialog.fields_dict[fieldname];
				if (field) {
					field.df.onchange = checar_duplicidade;
				}
			});
		}
	};
});
