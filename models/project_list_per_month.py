from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ProjectListPerMonth(models.Model):
    _name = 'project.list.per.month'
    _description = 'Project List Per Month'

    project_code = fields.Many2one('project.master', string='Project Code')
    employee_assignment_id = fields.Many2many('project.employee.assign', string='Employee Assignment')

    year = fields.Many2one("year.master", help='Unique Key', index=True, store=True)
    month = fields.Many2one("month.master", help='Unique Key', index=True, store=True)
    op_hours_planned = fields.Integer(string='OP Hours Planned', compute='_compute_hours_costs', store=True)
    op_hours_actual = fields.Integer(string='OP Hours Actual', compute='_compute_hours_costs', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'JPY')], limit=1), readonly=True)
    planned_cost = fields.Monetary(string='Planned Cost', compute='_compute_hours_costs', store=True)
    actual_cost = fields.Monetary(string='Actual Cost', compute='_compute_hours_costs', store=True)

    @api.depends('project_code', 'month', 'employee_assignment_id')
    def _compute_hours_costs(self):
        for record in self:
            total_planned_hours = sum(record.employee_assignment_id.mapped('op_hours_planned'))
            total_actual_hours = sum(record.employee_assignment_id.mapped('op_hours_actual'))

            record.op_hours_planned = total_planned_hours
            record.op_hours_actual = total_actual_hours

            employee_records = self.env['project.list.per.month.employee'].search([
                ('project_code', '=', record.project_code.id),
                ('year', '=', record.year.id),
                ('month', '=', record.month.id)
            ])

            _logger.info(f"Employee Records: {employee_records}")
            record.planned_cost = sum(employee_records.mapped('planned_cost'))
            record.actual_cost = sum(employee_records.mapped('actual_cost'))   

    def action_view_project_list_per_month_employee(self):
        return {
            'name': 'Employee on month %s of year %s' % (self.month.month, self.year.year),
            'type': 'ir.actions.act_window',
            'res_model': 'project.list.per.month.employee',
            'view_mode': 'tree',
            'view_id': self.env.ref('project-assign-system.view_project_list_per_month_employee_tree').id,
            'domain': [('project_code', '=', self.project_code.id), ('year', '=', self.year.id), ('month', '=', self.month.id)],
            'target': 'current',
        }
