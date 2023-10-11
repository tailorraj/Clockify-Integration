import frappe
import requests

def validate(self,method):
	sync_project(self)


def sync_project(self):
	workspace_id = frappe.db.get_single_value('Clockify Global Settings', 'workspace_id')
	if not workspace_id:
		frappe.msgprint("Workspace ID Needed From Clockify Global Settings!")
		return
	user_key = frappe.db.get_single_value('Clockify Global Settings', 'clockify_key')
	if not user_key:
		frappe.msgprint("Clockify Key Needed From Clockify Global Settings!")
		return

	url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects"

	headers = {
		"X-Api-Key": user_key,
		"Content-Type": "application/json",
		"Accept": "application/json"
	}

	data = {"name": self.project_name}

	try:
		response = requests.post(url, headers=headers, json=data)

		if response.status_code == 201:
			frappe.msgprint(f"Project '{self.project_name}' created successfully in Clockify.")
		elif response.status_code == 400:
			frappe.msgprint(f"Project '{self.project_name}' already exists in Clockify.")
		else:
			frappe.throw(f"Failed to create project '{self.project_name}'. Status code: {response.status_code}, Error: {response.text}")
			
	except requests.exceptions.RequestException as e:
		frappe.log_error(message = frappe.traceback(),title='Post Call Syncing Project Conflict')
		frappe.throw("An error occurred while syncing projects. Please check the error log for details.")
	except Exception as e:
		frappe.log_error(message = e,title='Syncing Project Conflicts')
		frappe.throw("An unexpected error occurred. Please check the error log for details.")