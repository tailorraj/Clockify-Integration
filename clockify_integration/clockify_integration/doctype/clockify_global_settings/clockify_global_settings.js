// Copyright (c) 2023, Raaj Tailor and contributors
// For license information, please see license.txt

frappe.ui.form.on('Clockify Global Settings', {
	refresh: function(frm) {
		frm.add_custom_button(__("Sync Project"), function() {
			frappe.call({
				method: 'clockify_integration.clockify_integration.doctype.clockify_global_settings.clockify_global_settings.sync_project',
				args: {
					'workspace_id': frm.doc.workspace_id
				},
				freeze: true,
				callback: (r) => {
					console.log(r.message)
				}
			})
		});

		frm.add_custom_button(__('Sync Employee Timesheet'), function(){
			let d = new frappe.ui.Dialog({
				title: 'Enter details',
				fields: [
					{
						label: 'For Date',
						fieldname: 'for_date',
						fieldtype: 'Date',
						reqd: 1
					}
				],
				primary_action_label: 'Submit',
				primary_action(values) {
					console.log(values.for_date);
					frappe.call({
						method: 'clockify_integration.clockify_integration.doctype.clockify_global_settings.clockify_global_settings.sync_employee_timesheet',
						args: {
							from_date: values.for_date
						},
						// disable the button until the request is completed
						btn: $('.primary-action'),
						// freeze the screen until the request is completed
						freeze: true,
						callback: (r) => {
							// on success
							console.log(r)
							
							d.hide();
						},
						error: (r) => {
							// on error
						}
					})
					
				}
			});
			
			d.show();
		});
	}
});
