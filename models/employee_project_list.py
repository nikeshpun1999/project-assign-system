from odoo import models, fields, api

class EmployeeProjectList(models.Model):
    _name = "employee.project.list"
    _description = "Employee Project List"

    employee_code = fields.Many2one("employee.master", help='Unique Key', index=True)
    employee_assignment_id = fields.Many2one('project.employee.assign', string='Employee Assignment')

    project_code = fields.Many2one('project.master', help='Unique Key', index=True, context={'show_name': True})
    project_name = fields.Char(related='project_code.name', store=True, readonly=True)
    op_hours_planned = fields.Integer(string='OP Planned Hours', compute='_compute_hours', store=True)
    op_hours_actual = fields.Integer(string='OP Actual Hours', compute='_compute_hours', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'JPY')], limit=1), readonly=True)
    planned_cost = fields.Monetary(string='Planned Cost', compute='_compute_costs', store=True)
    actual_cost = fields.Monetary(string='Actual Cost', compute='_compute_costs', store=True)

    def _compute_hours(self):
        for record in self:
            assignments = self.env['project.employee.assign'].search([
                ('employee_code', '=', record.employee_code.id),
                ('project_code', '=', record.project_code.id),
            ])
            
            planned_hours = sum(assignments.mapped('op_hours_planned'))
            actual_hours = sum(assignments.mapped('op_hours_actual'))

            record.op_hours_planned = planned_hours
            record.op_hours_actual = actual_hours

    def _compute_costs(self):
        for record in self:
            if record.employee_code and record.employee_code.class_code:
                unit_price = record.employee_code.class_code.unit_price
                
                record.planned_cost = unit_price * record.op_hours_planned if unit_price else 0
                record.actual_cost = unit_price * record.op_hours_actual if unit_price else 0
            else:
                record.planned_cost = 0
                record.actual_cost = 0

    def action_view_employee_project_list_per_month(self):
        return {
            'name': '%s' % (self.project_code.name),
            'type': 'ir.actions.act_window',
            'res_model': 'employee.project.list.per.month',
            'view_mode': 'tree,pivot',
            # 'view_id': self.env.ref('project_employee_assignment_system.view_employee_project_list_per_month_tree').id,
            'domain': [('project_code', '=', self.project_code.id), ('employee_code', '=', self.employee_code.id)],
            'target': 'current',
        }
