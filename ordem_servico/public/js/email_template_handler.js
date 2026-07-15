$(document).ready(function () {
	const Composer = frappe.views && frappe.views.CommunicationComposer;
	if (!Composer) return;

	const _orig_make = Composer.prototype.make;
	Composer.prototype.make = function () {
		_orig_make.apply(this, arguments);
		const me = this;
		const field = me.dialog.fields_dict.email_template;
		if (!field) return;

		field.df.onchange = function () {
			if (me.dialog.get_value("email_template") === "Pedido de item") {
				me.dialog.set_value("recipients", "assistencia@eranalitica.com.br");
			}
		};
	};
});
