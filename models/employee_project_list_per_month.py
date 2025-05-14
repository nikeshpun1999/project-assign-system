from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class EmployeeProjectListPerMonth(models.Model):
    _name = 'employee.project.list.per.month'
    _description = 'Employee Project List Per Month'

    project_code = fields.Many2one('project.master', string='Project Code')
    employee_code = fields.Many2one('employee.master', string='Employee Code')
    employee_assignment_id = fields.Many2one('project.employee.assign', string='Employee Assignment')

    year = fields.Many2one("year.master", help='Unique Key', index=True, store=True, readonly=True)
    month = fields.Many2one("month.master", help='Unique Key', index=True, store=True, readonly=True)
    op_hours_planned = fields.Integer(string='OP Hours Planned', compute='_compute_hours', store=True)
    op_hours_actual = fields.Integer(string='OP Hours Actual', compute='_compute_hours', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'JPY')], limit=1), readonly=True)
    planned_cost = fields.Monetary(string='Planned Cost', compute='_compute_costs', store=True)
    actual_cost = fields.Monetary(string='Actual Cost', compute='_compute_costs', store=True)
    
    @api.depends('project_code', 'employee_assignment_id')
    def _compute_hours(self):
        for record in self:
            total_planned_hours = sum(record.employee_assignment_id.mapped('op_hours_planned'))
            total_actual_hours = sum(record.employee_assignment_id.mapped('op_hours_actual'))

            record.op_hours_planned = total_planned_hours
            record.op_hours_actual = total_actual_hours

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
