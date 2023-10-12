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

			frappe.call({
				method: 'clockify_integration.clockify_integration.doctype.clockify_global_settings.clockify_global_settings.sync_employee_timesheet',
				args: {
					'from_date': frappe.datetime.nowdate()
				},
				freeze: true,
				callback: (r) => {
					// on success
					console.log(r)
					
				},
			})
			
		});


		frm.add_custom_button(__('Sync Employee Attendance'), function(){

			frappe.call({
				method: 'clockify_integration.clockify_integration.doctype.clockify_global_settings.clockify_global_settings.sync_employee_attendance_based_on_timesheet',
				args: {
					from_date: frappe.datetime.nowdate()
				},
				freeze: true,
				callback: (r) => {
					// on success
					console.log(r)
					
					d.hide();
				},
			})
			
		});
	}
});
