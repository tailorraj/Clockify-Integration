from . import __version__ as app_version

app_name = "clockify_integration"
app_title = "Clockify Integration"
app_publisher = "Raaj Tailor"
app_description = "Clockify Integration"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "raaj@akhilaminc.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/clockify_integration/css/clockify_integration.css"
# app_include_js = "/assets/clockify_integration/js/clockify_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/clockify_integration/css/clockify_integration.css"
# web_include_js = "/assets/clockify_integration/js/clockify_integration.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "clockify_integration/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Timesheet" : "clockify_integration/override_doctype/timesheet/timesheet.js"
	}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "clockify_integration.install.before_install"
# after_install = "clockify_integration.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "clockify_integration.uninstall.before_uninstall"
# after_uninstall = "clockify_integration.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "clockify_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

doc_events = {
	"Project": {
		"validate": "clockify_integration.clockify_integration.override_doctype.project.project.validate",
	}
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    
    "cron": {
        "0 23 * * *": [
            "clockify_integration.clockify_integration.doctype.clockify_global_settings.clockify_global_settings.sync_employee_timesheet"
        ],
        "30 23 * * *": [
            "clockify_integration.clockify_integration.doctype.clockify_global_settings.clockify_global_settings.sync_employee_attendance_based_on_timesheet"
        ]
    }
}
# scheduler_events = {
#	"all": [
#		"clockify_integration.tasks.all"
#	],
#	"daily": [
#		"clockify_integration.tasks.daily"
#	],
#	"hourly": [
#		"clockify_integration.tasks.hourly"
#	],
#	"weekly": [
#		"clockify_integration.tasks.weekly"
#	]
#	"monthly": [
#		"clockify_integration.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "clockify_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "clockify_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "clockify_integration.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"clockify_integration.auth.validate"
# ]

