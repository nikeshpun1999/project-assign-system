from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ProjectList(models.Model):
    _name = "project.list"
    _description = "Project List"
    
    employee_assignment_id = fields.Many2many('project.employee.assign', string='Employee Assignment')

    project_employee_assign_per_month_id = fields.One2many('project.employee.assign.per.month','project_code')
    project_list_per_month_id = fields.One2many('project.list.per.month','project_code')



    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    project_code = fields.Many2one("project.master", required=True, help='Unique Key', index=True)
    project_name = fields.Char(related='project_code.name', store=True, readonly=False)
    op_hours_planned = fields.Integer(string='OP Hours Planned', compute='_compute_hours_costs', store=True)
    op_hours_actual = fields.Integer(string='OP Hours Actual', compute='_compute_hours_costs', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'JPY')], limit=1), readonly=True)
    planned_cost = fields.Monetary(string='Planned Cost', compute='_compute_hours_costs', store=True)
    actual_cost = fields.Monetary(string='Actual Cost', compute='_compute_hours_costs', store=True)

    _sql_constraints = [
        ('unique_project_code', 'UNIQUE(project_code)', 'The project code must be unique.')
    ]

    def _compute_sequence_no(self):
        all_records = self.search([])
        for index, record in enumerate(all_records, start=1):
            record.no = index

    @api.depends('project_code')
    def _compute_hours_costs(self):
        for record in self:

            assignments = self.env['project.employee.assign'].search([
                ('project_code', '=', record.project_code.id),
            ])

            total_planned_hours = sum(assignments.mapped('op_hours_planned'))
            total_actual_hours = sum(assignments.mapped('op_hours_actual'))

            record.op_hours_planned = total_planned_hours
            record.op_hours_actual = total_actual_hours


            employee_records = self.env['project.list.per.month.employee'].search([
                ('project_code', '=', record.project_code.id),
            ])

            _logger.info(f"Employee Records: {employee_records}")
            record.planned_cost = sum(employee_records.mapped('planned_cost'))
            record.actual_cost = sum(employee_records.mapped('actual_cost'))  

    # def action_view_project_assignments_per_month(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': f'Employees in {self.project_name} List',
    #         'res_model': 'project.employee.assign.per.month',
    #         'view_mode': 'tree',
    #         'view_id': self.env.ref('project_employee_assignment_system.view_project_assign_per_month_tree').id,
    #         'domain': [('project_code', '=', self.project_code.id)],
    #         'context': {'default_project_code': self.project_code.id},
    #     }

    def action_view_project_assignments_per_month(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Employees in {self.project_name} List',
            'res_model': 'project.employee.assign.per.month',
            'view_mode': 'tree',
            'view_id': self.env.ref('project-assign-system.view_project_assign_per_month_tree').id,
            'search_view_id': self.env.ref('project-assign-system.view_project_assign_per_month_search').id,
            'domain': [('project_code', '=', self.project_code.id)],
            'context': {
                'default_project_code': self.project_code.id,
                'search_default_filter_year': 1,
            },
        }

    def action_view_project_list_per_month(self):
        self.ensure_one()

        assignments = self.env['project.employee.assign'].search([
            ('project_code', '=', self.project_code.id)
        ])

        assignments_by_month = {}
        for assignment in assignments:
            month_key = (assignment.year.id, assignment.month.id)
            if month_key not in assignments_by_month:
                assignments_by_month[month_key] = self.env['project.employee.assign']
            assignments_by_month[month_key] |= assignment

        for (year_id, month_id), month_assignments in assignments_by_month.items():

            values = {
                'project_code': self.project_code.id,
                'year': year_id,
                'month': month_id,
                'employee_assignment_id': [(6, 0, month_assignments.ids)],
            }

            existing_record = self.env['project.list.per.month'].search([
                ('project_code', '=', self.project_code.id),
                ('year', '=', year_id),
                ('month', '=', month_id)
            ])

            if existing_record:
                existing_record.write(values)
            else:
                self.env['project.list.per.month'].create(values)

        return {
            'name': f'{self.project_name} Summary',
            'type': 'ir.actions.act_window',
            'res_model': 'project.list.per.month',
            'view_mode': 'tree,pivot',
            'domain': [('project_code', '=', self.project_code.id)],
            'target': 'current',
        }
