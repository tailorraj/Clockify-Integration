import frappe
import requests
from datetime import datetime, timedelta

# ---------------------------------Sync Employee Timesheet----------------------------------

@frappe.whitelist()
def sync_employee_timesheet():
	current_date = frappe.utils.today()
	from_date = (datetime.strptime(current_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
	try:
		start_datetime, end_datetime = prepare_datetimes(from_date)
		workspace_id = get_clockify_workspace_id()

		employee_data = get_enabled_clockify_users()
		
		if not employee_data:
			frappe.throw("No Employees Found")
		
		for employee in employee_data:
			time_entries = fetch_clockify_time_entries(workspace_id, employee, start_datetime, end_datetime)

			if time_entries:
				try:
					create_timesheet_for_employee(employee, time_entries, start_datetime)
				except Exception as e:
					frappe.msgprint(f"Error processing timesheet for {employee.employee_id}: {str(e)}")
					continue
			else:
				frappe.msgprint("No Timesheet Found for the Selected Date")
				continue		

	except Exception as e:
		frappe.log_error(message = frappe.get_traceback(),title='Syncing Employee Timesheet Conflicts')
		frappe.throw("Error Occured While Creating Timesheets!")


def prepare_datetimes(from_date):
	start_datetime = datetime.strptime(from_date, '%Y-%m-%d').replace(hour=0, minute=0, second=1)
	end_datetime = start_datetime.replace(hour=23, minute=59, second=59)
	start_datetime_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
	end_datetime_str = end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
	return start_datetime_str, end_datetime_str

def get_clockify_workspace_id():
	return frappe.db.get_single_value('Clockify Global Settings', 'workspace_id')

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

def create_timesheet_for_employee(employee, time_entries,start_datetime):
	try:
		workspace_id = get_clockify_workspace_id()
		existing_timesheets = get_existing_timesheets(employee, start_datetime)

		if not existing_timesheets:
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
			ts_doc.submit()
			frappe.msgprint("Timesheet Created Successfully For The Selected Date")
		else:
			frappe.msgprint("Timesheet already exists for the employee for the selected date!")	
	except Exception as e:
		frappe.throw(f"Error creating timesheet: {str(e)}")

def get_existing_timesheets(employee, start_datetime):
    timesheets = frappe.db.get_list("Timesheet", filters={"employee": employee.employee_id, "start_date": start_datetime})
    return [frappe.get_doc("Timesheet", ts["name"]) for ts in timesheets]
 

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

# ---------------------------------Sync Employee Timesheet----------------------------------


# ---------------------------------Sync Employee Attendance Based On Timesheet----------------------------------


@frappe.whitelist()
def sync_employee_attendance_based_on_timesheet():
	current_date = frappe.utils.today()
	from_date = (datetime.strptime(current_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
	try:
		employee_shift_timings = frappe.get_all("Employee Shift Timings", fields=["min_working_hours_for_half_day", "min_working_hours_for_present", "employee_name", "employee", "holidays"])

		for employee in employee_shift_timings:
			timesheet = frappe.get_value('Timesheet', 
				{'employee': employee.employee, 'start_date': from_date},
				['total_hours', 'employee_name'], as_dict=True)

			if timesheet and timesheet.total_hours is not None:
				attendance_status = "Present" if timesheet.total_hours >= employee.min_working_hours_for_present else "Half Day" if timesheet.total_hours >= employee.min_working_hours_for_half_day else "Absent"
				if not frappe.db.exists("Attendance", {"employee": employee.employee, 'attendance_date': from_date}):
					attendance_doc = frappe.get_doc({
						"doctype":"Attendance",
						"employee": employee.employee,
						"attendance_date": from_date,
						"status": attendance_status,
						"working_hours": timesheet.total_hours if timesheet and timesheet.total_hours is not None else 0,
						"leave_type": "Leave Without Pay" if attendance_status == "Half Day" else None
					})
					attendance_doc.insert(ignore_permissions=True)
					attendance_doc.submit()
				frappe.msgprint(f"{employee.employee_name} is {attendance_status} for {from_date}")
			else:
				holiday_doc = frappe.get_doc('Holiday List', {'name':employee.holidays})

				if not any(from_date == str(hd.holiday_date) for hd in holiday_doc.holidays):
					frappe.msgprint(f"{employee.employee_name} is absent for {from_date}")

					if not frappe.db.exists("Attendance", {"employee": employee.employee, 'attendance_date': from_date}):
						attendance_doc = frappe.get_doc({
							"doctype":"Attendance",
							"employee": employee.employee,
							"attendance_date": from_date,
							"status": "Absent",
							"working_hours": 0,
							"leave_type": None
						})
						attendance_doc.insert(ignore_permissions=True)
						attendance_doc.submit()
						# frappe.msgprint(f"{employee.employee_name} is {attendance_status} for {from_date}")

	
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title='Syncing Employee Attendance Based On Timesheet Conflicts')
		frappe.msgprint("Error occurred while creating attendance!")


# ---------------------------------Sync Employee Attendance Based On Timesheet----------------------------------