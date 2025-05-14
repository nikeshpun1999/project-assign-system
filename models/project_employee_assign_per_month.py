from odoo import models, fields, api

class ProjectEmployeeAssignPerMonth(models.Model):
    _name = "project.employee.assign.per.month"
    _description = "Project Employee Assign Per Month"

    project_code = fields.Many2one("project.master", required=True, index=True, context={'show_name': True})
    employee_code = fields.Many2one("employee.master", required=True, index=True, context={'show_name': True})
    year = fields.Many2one("year.master", required=True, index=True)
    month_01 = fields.Integer(string='01', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_02 = fields.Integer(string='02', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_03 = fields.Integer(string='03', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_04 = fields.Integer(string='04', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_05 = fields.Integer(string='05', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_06 = fields.Integer(string='06', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_07 = fields.Integer(string='07', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_08 = fields.Integer(string='08', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_09 = fields.Integer(string='09', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_10 = fields.Integer(string='10', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_11 = fields.Integer(string='11', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    month_12 = fields.Integer(string='12', compute='_compute_hours', inverse='_inverse_hours', default=0, store=True)
    show_actual = fields.Boolean(
        string="Show Actual Hours",
        default=True,
        help="Toggle between Actual and Planned hours"
    )
    related_assignment_ids = fields.One2many(
        comodel_name='project.employee.assign',
        inverse_name='project_code',
        string='Related Assignments',
        compute='_compute_related_assignments'
    )

    display_hours = fields.Char(
        string="Displayed Hours",
        compute="_compute_display_hours",
        store=True
    )

    _sql_constraints = [
        ('unique_project_employee_year', 'UNIQUE(project_code, employee_code, year)', 'The combination of project code, employee code and year must be unique.')
    ]

    @api.depends('show_actual', 'related_assignment_ids.op_hours_actual', 'related_assignment_ids.op_hours_planned')
    def _compute_hours(self):
        for record in self:
            assignments = self.env['project.employee.assign'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', record.employee_code.id), 
                ('year', '=', record.year.id)
            ])

            field_key = 'op_hours_actual' if record.show_actual else 'op_hours_planned'
            assignment_map = {assignment.month.month: getattr(assignment, field_key, 0.0) for assignment in assignments}

            for month in range(1, 13):
                month_field = f'month_{month:02d}'
                
                current_value = getattr(record, month_field)

                if month in assignment_map:
                    setattr(record, month_field, assignment_map[month])
                else:
                    if current_value in (None, 0.0):
                        setattr(record, month_field, 0.0)

    @api.depends('month_01', 'month_02', 'month_03', 'month_04', 'month_05', 'month_06', 'month_07', 'month_08', 'month_09', 'month_10', 'month_11', 'month_12')
    def _inverse_hours(self):
        for record in self:
            for month in range(1, 13):
                month_field = f'month_{month:02d}'
                month_value = getattr(record, month_field)

                assignment = self.env['project.employee.assign'].search([
                    ('project_code', '=', record.project_code.id),
                    ('employee_code', '=', record.employee_code.id),
                    ('year', '=', record.year.id),
                    ('month.month', '=', month)
                ], limit=1)

                if assignment:
                    if record.show_actual:
                        assignment.op_hours_actual = month_value
                    else:
                        assignment.op_hours_planned = month_value
                else:
                    if month_value != 0.0:
                        # default_year = self.env['year.master'].search([('default_flag', '=', True)], limit=1)
                        # if not default_year:
                        #     raise ValueError("Default year is not set. Please ensure that a default year is marked in Year Master.")

                        self.env['project.employee.assign'].create({
                            'project_code': record.project_code.id,
                            'employee_code': record.employee_code.id,
                            'year': record.year.id,
                            'month': self.env['month.master'].search([('month', '=', month)], limit=1).id,
                            'op_hours_planned': month_value if not record.show_actual else 0.0,
                            'op_hours_actual': month_value if record.show_actual else 0.0,
                        })
    
    def action_toggle_hours(self):
            """Toggle between showing Actual and Planned hours."""
            all_records = self.search([])
            for record in all_records:
                    record.show_actual = not record.show_actual

    @api.depends('show_actual')
    def _compute_display_hours(self):
        for record in self:
            record.display_hours = "Actual Hours" if record.show_actual else "Planned Hours"


    @api.depends('project_code', 'employee_code', 'year')
    def _compute_related_assignments(self):
        for record in self:
            record.related_assignment_ids = self.env['project.employee.assign'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', record.employee_code.id),
                ('year', '=', record.year.id)
            ])
    
    def action_view_project_list_employee_summary(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Summary of {self.employee_code.name}-san',
            'res_model': 'project.list.employee.summary',
            'view_mode': 'tree',
            'view_id': self.env.ref('project-assign-system.view_project_list_employee_summary_tree').id,
            'domain': [
                        '&',
                        ('employee_code', '=', self.employee_code.id),
                        ('project_code', '=', self.project_code.id),
                        ('year', '=', self.year.id)
                    ],            
        }

    def action_view_project_employee_assign(self):
        # project_code = self.project_code.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Employee',
            'res_model': 'project.employee.assign',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('project-assign-system.view_project_employee_assign_form').id,
            'context': {
                'default_project_code': self.env.context.get('active_id'),
            },
        }
