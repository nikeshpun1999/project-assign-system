from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class EmployeeList(models.Model):
    _name = "employee.list"
    _description = "Employee List"
    
    employee_assignment_id = fields.Many2many('project.employee.assign', string='Employee Assignment')

    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    employee_code = fields.Many2one("employee.master", required=True, help='Unique Key', index=True)
    employee_name = fields.Char(related='employee_code.name', store=True, readonly=False)
    total_projects = fields.Integer(string='Total Projects', compute='_compute_total_projects', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'JPY')], limit=1), readonly=True)
    total_earning = fields.Monetary(string='Total Earning', compute='_compute_total_earning', store=True)

    _sql_constraints = [
        ('unique_employee_code', 'UNIQUE(employee_code)', 'The employee code must be unique.')
    ]

    def _compute_sequence_no(self):
        for record in self:
            record.no = record.employee_code.no if record.employee_code else 0

    def _compute_total_projects(self):
        for record in self:
            assignments = self.env['project.employee.assign'].search([
                ('employee_code', '=', record.employee_code.id),
            ])
            _logger.info("Assignments found for employee %s: %s", record.employee_code.name, assignments)
            
            unique_projects = len(assignments.mapped('project_code'))
            record.total_projects = unique_projects

    def _compute_total_earning(self):
        for record in self:
            assignments = self.env['project.employee.assign'].search([
                ('employee_code', '=', record.employee_code.id),
            ])
            total_hours_worked = sum(assignments.mapped('op_hours_actual'))
            if record.employee_code and record.employee_code.class_code:
                unit_price = record.employee_code.class_code.unit_price   
                record.total_earning = unit_price * total_hours_worked if unit_price else 0
            else:
                record.total_earning = 0

    def action_view_employee_project_list(self):
        return {
            'name': 'Project list of %s' % (self.employee_code.name),
            'type': 'ir.actions.act_window',
            'res_model': 'employee.project.list',
            'view_mode': 'tree,pivot',
            'domain': [('employee_code', '=', self.employee_code.id)],
            'target': 'current',
        }