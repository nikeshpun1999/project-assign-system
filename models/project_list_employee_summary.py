from odoo import models, fields, api

class ProjectListEmployeeSummary(models.Model):
    _name = "project.list.employee.summary"
    _description = "Project List Employee Summary"

    employee_assignment_id = fields.Many2one('project.employee.assign', string='Employee Assignment')
    project_code = fields.Many2one("project.master", required=True, help='Unique Key', index=True)
    employee_code = fields.Many2one("employee.master", required=True, help='Unique ', index=True)

    year = fields.Many2one("year.master", required=True, help='Unique Key', index=True)
    month = fields.Many2one("month.master", required=True, help='Unique Key', index=True)
    op_hours_planned = fields.Integer(required=True)
    op_hours_actual = fields.Integer(required=True)

    _sql_constraints = [
        ('unique_project_employee_year_month', 'UNIQUE(project_code, employee_code, year, month)', 'The combination of project code, employee code, year, and month must be unique.')
    ]
