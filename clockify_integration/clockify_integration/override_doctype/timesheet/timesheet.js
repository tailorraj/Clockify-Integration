frappe.ui.form.on('Timesheet', {
	refresh: function(frm) {
		frm.add_custom_button(__('Sync Clockify'), function(){
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
                        method: 'clockify_integration.clockify_integration.override_doctype.timesheet.timesheet.sync_clocify',
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
                            if(r.message){
                                if(cur_frm.get_field("time_logs").grid.grid_rows[0]){
                                    cur_frm.get_field("time_logs").grid.grid_rows[0].remove();
                                }
                                
                                var total_diff = 0
                                for(var i in r.message){
                                    var childTable = cur_frm.add_child("time_logs");
                                    childTable.activity_type="Development"
                                    childTable.from_time=r.message[i].from_time
                                    childTable.to_time=r.message[i].to_time
                                    childTable.hours=r.message[i].diff
                                    childTable.description=r.message[i].description
                                    total_diff += r.message[i].diff
                                }
                                frm.doc.total_hours = total_diff
                                refresh_field("total_hours")
                                refresh_field("time_logs")
                            }
                            
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
})