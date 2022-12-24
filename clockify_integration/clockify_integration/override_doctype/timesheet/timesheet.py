import frappe
import requests
from datetime import datetime, timedelta
import json

@frappe.whitelist()
def sync_clocify(from_date):
    naive_dt = datetime.strptime(from_date, '%Y-%m-%d')
    naive_dt = naive_dt.replace(hour=0, minute=0, second=1)
    naive_end_dt = naive_dt.replace(hour=23, minute=59, second=59)
    naive_dt = naive_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    naive_end_dt = naive_end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    # return naive_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    workspace_id =  frappe.db.get_single_value('Task List Settings', 'workspace_id')
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")

    if employee:   
        user_id = frappe.db.get_value("Task List Setting Users", {"erp_user": employee}, ["clockify_id", "clockify_key"], as_dict=1)
        if user_id:
            str_url = "https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{user_id}/time-entries?start={date}&end={end_dt}".format(workspace_id = workspace_id, user_id = user_id.clockify_id, date = naive_dt, end_dt = naive_end_dt)

            url = str_url
            body = {
            }

            header={
                "X-Api-Key": user_id.clockify_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            time_sheet = []
            # return body
            req = requests.get(url=url, data=body, headers=header)
            if req.status_code == 200:
                if req.json():
                    # return req.json()
                    for item in req.json():
                        start_dt = datetime.strptime(item["timeInterval"]["start"], '%Y-%m-%dT%H:%M:%SZ')
                        start_dt = start_dt + timedelta(hours=5)
                        start_dt = start_dt + timedelta(minutes=30)
                        end_dt = datetime.strptime(item["timeInterval"]["end"], '%Y-%m-%dT%H:%M:%SZ')
                        end_dt = end_dt + timedelta(hours=5)
                        end_dt = end_dt + timedelta(minutes=30)

                        delta = end_dt - start_dt
                        sec = delta.total_seconds()
                        hours = sec / (60 * 60)
                        # ts = frappe.new_doc("Timesheet")
                        # ts.employee = employee
                        # ts.append("time_logs", {
                        #     "activity_type" : "Development",
                        #     "from_time" : start_dt,
                        #     "to_time" : end_dt
                        # })     

                        # ts.save(ignore_permissions=True)
                        log = {
                            "from_time": start_dt,
                            "to_time": end_dt,
                            "description": item["description"],
                            "diff": float("%0.4f" % (hours)) 
                        }
                        time_sheet.append(log)

                else:
                    frappe.msgprint("No Timesheet Found for the Selected Date")
                    return

            return time_sheet
        else:
            frappe.throw("No Clocify Id Assigned to the User")
    
    else:
        frappe.throw("Employee Not Creeated for you")