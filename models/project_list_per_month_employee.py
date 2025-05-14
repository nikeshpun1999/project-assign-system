from odoo import models, fields, api

class ProjectListPerMonthEmployee(models.Model):
    _name = 'project.list.per.month.employee'
    _description = 'Project List Per Month Employee'

    project_code = fields.Many2one('project.master', string='Project Code', required=True, help='Reference to the Project Master')
    month = fields.Many2one("month.master", required=True, help='Unique Key', index=True)
    year = fields.Many2one("year.master", required=True, help='Unique Key', index=True)
    employee_assignment_id = fields.Many2one('project.employee.assign', string='Employee Assignment')

    employee_code = fields.Many2one("employee.master", help='Unique Key', index=True, context={'show_name': True})
    op_hours_planned = fields.Integer(related='employee_assignment_id.op_hours_planned', string='OP Planned Hours')
    op_hours_actual = fields.Integer(related='employee_assignment_id.op_hours_actual', string='OP Actual Hours')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'JPY')], limit=1), readonly=True)
    planned_cost = fields.Monetary(string='Planned Cost', compute='_compute_costs', store=True)
    actual_cost = fields.Monetary(string='Actual Cost', compute='_compute_costs', store=True)

    @api.depends('employee_code', 'op_hours_planned', 'op_hours_actual')
    def _compute_costs(self):
        for record in self:
            if record.employee_code and record.employee_code.class_code:
                unit_price = record.employee_code.class_code.unit_price
                
                record.planned_cost = unit_price * record.op_hours_planned if unit_price else 0
                record.actual_cost = unit_price * record.op_hours_actual if unit_price else 0
            else:
                record.planned_cost = 0
                record.actual_cost = 0
