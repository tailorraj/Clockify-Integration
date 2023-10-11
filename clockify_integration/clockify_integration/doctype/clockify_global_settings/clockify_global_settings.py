# Copyright (c) 2023, Raaj Tailor and contributors
# For license information, please see license.txt

import frappe
import requests
from datetime import datetime, timedelta
from frappe.model.document import Document

class ClockifyGlobalSettings(Document):
	pass

# ---------------------------------Sync Project----------------------------------

@frappe.whitelist()
def sync_project(workspace_id):
	user_key = frappe.db.get_single_value('Clockify Global Settings', 'clockify_key')
	if not user_key:
		frappe.msgprint("Clockify Key Needed From Clockify Global Settings!")
		return

	projects = frappe.get_all('Project', filters={'status': 'Open'}, pluck='project_name')
	if not projects:
		frappe.msgprint("No open projects to sync with Clockify.")
		return

	url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects"

	headers = {
		"X-Api-Key": user_key,
		"Content-Type": "application/json",
		"Accept": "application/json"
	}
	for project_name in projects:
		data = {"name": project_name}

		try:
			response = requests.post(url, headers=headers, json=data)

			if response.status_code == 201:
				frappe.msgprint(f"Project '{project_name}' created successfully in Clockify.")
			elif response.status_code == 400:
				frappe.msgprint(f"Project '{project_name}' already exists in Clockify.")
			else:
				frappe.throw(f"Failed to create project '{project_name}'. Status code: {response.status_code}, Error: {response.text}")
		except requests.exceptions.RequestException as e:
			frappe.log_error(message = frappe.traceback(),title='Post Call Syncing Project Conflict')
			frappe.throw("An error occurred while syncing projects. Please check the error log for details.")
		except Exception as e:
			frappe.log_error(message = e,title='Syncing Project Conflicts')
			frappe.throw("An unexpected error occurred. Please check the error log for details.")

# ---------------------------------Sync Project----------------------------------


# ---------------------------------Sync Employee Timesheet----------------------------------

@frappe.whitelist()
def sync_employee_timesheet(from_date):
    try:
        start_datetime, end_datetime = prepare_datetimes(from_date)
        workspace_id = get_clockify_workspace_id()

        employee_data = get_enabled_clockify_users()
        
        if not employee_data:
            frappe.throw("No Employees Found")
        
        for employee in employee_data:
            time_entries = fetch_clockify_time_entries(workspace_id,employee, start_datetime, end_datetime)

            if time_entries:
                create_timesheet_for_employee(employee, time_entries)
            else:
                frappe.msgprint("No Timesheet Found for the Selected Date")
    except Exception as e:
        frappe.throw(str(e))

def prepare_datetimes(from_date):
    start_datetime = datetime.strptime(from_date, '%Y-%m-%d').replace(hour=0, minute=0, second=1)
    end_datetime = start_datetime.replace(hour=23, minute=59, second=59)
    start_datetime_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_datetime_str = end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    return start_datetime_str, end_datetime_str

def get_clockify_workspace_id():
    return frappe.db.get_single_value('Clockify Settings', 'workspace_id')

def get_enabled_clockify_users():
    return frappe.db.get_list('Clockify User', filters={'enable': '1'}, fields=["clockify_id", "clockify_key", "user_id", "employee_id"])

def fetch_clockify_time_entries(workspace_id,employee, start_datetime, end_datetime):
    try:
        url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{employee.clockify_id}/time-entries?start={start_datetime}&end={end_datetime}"

        headers = {
            "X-Api-Key": employee.clockify_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            frappe.throw("Clockify API Error")
    except Exception as e:
        frappe.throw(f"Error fetching Clockify time entries: {str(e)}")

def create_timesheet_for_employee(employee, time_entries):
    try:
        workspace_id = get_clockify_workspace_id()
        ts_doc = frappe.get_doc({
            'doctype': 'Timesheet',
            'status': 'Draft',
            'employee': employee.employee_id
        })

        for item in time_entries:
            start_dt, end_dt, hours, project_name = process_time_entry(item, employee,workspace_id)
            item_doc = frappe.get_doc({
                'doctype': 'Timesheet Detail',
                'activity_type': 'Development',
                'from_time': start_dt,
                'to_time': end_dt,
                'description': item["description"],
                'hours': hours,
                'project_name': project_name
            })
            ts_doc.append('time_logs', item_doc)

        ts_doc.insert(ignore_permissions=1)
        frappe.msgprint("Timesheet Created Successfully For The Selected Date")
    except Exception as e:
        frappe.throw(f"Error creating timesheet: {str(e)}")


 

def process_time_entry(item, employee,workspace_id):
    start_dt = datetime.strptime(item["timeInterval"]["start"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=5) + timedelta(minutes=30)
    end_dt = datetime.strptime(item["timeInterval"]["end"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=5) + timedelta(minutes=30)
    delta = end_dt - start_dt
    hours = delta.total_seconds() / (60 * 60)
    project_id = item['projectId']
    project_name = get_clockify_project_name(workspace_id, employee.clockify_key, project_id)
    return start_dt, end_dt, hours, project_name

def get_clockify_project_name(workspace_id, clockify_key, project_id):
    url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects/{project_id}"
    header = {
        "X-Api-Key": clockify_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        data = response.json()
        project_name = data.get('name')
        return project_name
    else:
        return None