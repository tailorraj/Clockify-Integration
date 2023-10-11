# Copyright (c) 2023, Raaj Tailor and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document

class ClockifyUser(Document):
	# pass

	def validate(self):
		workspace_id = frappe.db.get_single_value('Clockify Global Settings', 'workspace_id')
		if not workspace_id:
			frappe.throw("Please set Workspace ID in Clockify Global Settings!")

		user_id = self.clockify_key
		if not user_id:
			frappe.throw("Please Set Data of Clockify Key in Document!")

		try:
			url = f"https://api.clockify.me/api/workspaces/{workspace_id}/users/".format(workspace_id = workspace_id)

			headers = {
				"X-Api-Key": user_id,
				"Content-Type": "application/json",
				"Accept": "application/json"
			}

			response = requests.get(url, headers=headers)

			if response.status_code == 200:
				user_data = response.json()
				for item in user_data:
					if self.user_id == item.get('email'):
						self.clockify_id = item.get('id')
			else:
				frappe.throw(f"Clockify API request failed with status code {response.status_code}")

		except requests.exceptions.RequestException as e:
			frappe.throw(f"Error making a request to Clockify API: {str(e)}")
		except Exception as e:
			frappe.throw(f"An unexpected error occurred: {str(e)}")
					
