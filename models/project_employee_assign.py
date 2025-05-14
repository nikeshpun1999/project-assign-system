from odoo import models, fields, api

class ProjectEmployeeAssign(models.Model):
    _name = "project.employee.assign"
    _description = "Project Employee Assign"

    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    project_code = fields.Many2one("project.master", required=True, help='Unique Key', index=True)
    employee_code = fields.Many2one("employee.master", required=True, help='Unique ', index=True)
    year = fields.Many2one("year.master", required=True, help='Unique Key', index=True)
    month = fields.Many2one("month.master", required=True, help='Unique Key', index=True)
    op_hours_planned = fields.Integer(required=True)
    op_hours_actual = fields.Integer(required=True)

    _sql_constraints = [
        ('unique_project_employee_year_month', 'UNIQUE(project_code, employee_code, year, month)', 'The combination of project code, employee code, year, and month must be unique.')
    ]

    def _compute_sequence_no(self):
        all_records = self.search([])
        for index, record in enumerate(all_records, start=1):
            record.no = index

    @api.model
    def create(self, vals):
        record = super(ProjectEmployeeAssign, self).create(vals)

        existing_assignment = self.env['project.employee.assign.per.month'].search([
            ('project_code', '=', record.project_code.id),
            ('employee_code', '=', record.employee_code.id),
            ('year', '=', record.year.id)
        ], limit=1)

        if not existing_assignment:
            month_field = f'month_{str(record.month.month).zfill(2)}'

            self.env['project.employee.assign.per.month'].create({
                'project_code': record.project_code.id,
                'employee_code': record.employee_code.id,
                'year': record.year.id,
                month_field: record.op_hours_actual,
            })

        assignments = self.env['project.employee.assign'].search([
            ('project_code', '=', record.project_code.id),
            ('month', '=', record.month.id)
        ])

        for assignment in assignments:
            existing_list_entry = self.env['project.list.per.month.employee'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', record.employee_code.id),
                ('year', '=', record.year.id),
                ('month', '=', record.month.id)
            ], limit=1)

            if not existing_list_entry:
                self.env['project.list.per.month.employee'].create({
                    'project_code': record.project_code.id,
                    'year': record.year.id,
                    'month': record.month.id,
                    'employee_code': record.employee_code.id,
                    'employee_assignment_id': record.id,
                })

        for assignment in assignments:
            existing_list_entry = self.env['employee.project.list'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', assignment.employee_code.id)
            ], limit=1)

            if not existing_list_entry:
                self.env['employee.project.list'].create({
                    'project_code': record.project_code.id,
                    'employee_code': assignment.employee_code.id,
                    'employee_assignment_id': assignment.id,
                    'op_hours_planned': assignment.op_hours_planned,
                    'op_hours_actual': assignment.op_hours_actual,
                })

        for assignment in assignments:
            existing_list_entry = self.env['project.list.employee.summary'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', assignment.employee_code.id),
                ('year', '=', record.year.id),
                ('month', '=', record.month.id),
            ], limit=1)

            if not existing_list_entry:
                self.env['project.list.employee.summary'].create({
                    'project_code': record.project_code.id,
                    'employee_code': assignment.employee_code.id,
                    'year': record.year.id,
                    'month': record.month.id,
                    'employee_assignment_id': assignment.id,
                    'op_hours_planned': assignment.op_hours_planned,
                    'op_hours_actual': assignment.op_hours_actual,
                })
    
        for assignment in assignments:
            existing_list_entry = self.env['employee.project.list.per.month'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', assignment.employee_code.id),
                ('year', '=', record.year.id),
                ('month', '=', record.month.id),
            ], limit=1)

            if not existing_list_entry:
                self.env['employee.project.list.per.month'].create({
                    'project_code': record.project_code.id,
                    'employee_code': assignment.employee_code.id,
                    'year': record.year.id,
                    'month': record.month.id,
                    'employee_assignment_id': assignment.id,
                    'op_hours_planned': assignment.op_hours_planned,
                    'op_hours_actual': assignment.op_hours_actual,
                })
                
        employee_list = self.env['employee.list'].search([('employee_code', '=', record.employee_code.id)])
        if employee_list:
            employee_list._compute_total_projects()
            employee_list._compute_total_earning()

        employee_project_list = self.env['employee.project.list'].search([('employee_code', '=', record.employee_code.id), ('project_code', '=', record.project_code.id)])
        if employee_project_list:
            employee_project_list._compute_hours()
            employee_project_list._compute_costs()
        
        employee_project_list_per_month = self.env['employee.project.list.per.month'].search([('employee_code', '=', record.employee_code.id), ('project_code', '=', record.project_code.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
        if employee_project_list_per_month:
            employee_project_list_per_month._compute_hours()
            employee_project_list_per_month._compute_costs()
        
        project_list = self.env['project.list'].search([('project_code', '=', record.project_code.id)])
        if project_list:
            project_list._compute_hours_costs()

        return record

    def unlink(self):
        for record in self:
            assignment_per_month = self.env['project.employee.assign.per.month'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', record.employee_code.id)
            ], limit=1)

            if assignment_per_month:
                assignment_per_month.unlink()

            list_entries = self.env['project.list.per.month.employee'].search([
                ('project_code', '=', record.project_code.id),
                ('month', '=', record.month.id),
                ('employee_code', '=', record.employee_code.id),
                ('employee_assignment_id', '=', record.id)
            ])

            if list_entries:
                list_entries.unlink()

            employee_project_list_entries = self.env['employee.project.list'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', record.employee_code.id),
                ('employee_assignment_id', '=', record.id)
            ])

            if employee_project_list_entries:
                employee_project_list_entries.unlink()

            project_list_employee_summary_entries = self.env['project.list.employee.summary'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', record.employee_code.id),
                ('year', '=', record.year.id),
                ('month', '=', record.month.id),
                ('employee_assignment_id', '=', record.id)
            ])

            if project_list_employee_summary_entries:
                project_list_employee_summary_entries.unlink()

            employee_project_list_per_month_entries = self.env['employee.project.list.per.month'].search([
                ('project_code', '=', record.project_code.id),
                ('employee_code', '=', record.employee_code.id),
                ('year', '=', record.year.id),
                ('month', '=', record.month.id),
                ('employee_assignment_id', '=', record.id)
            ])

            if employee_project_list_per_month_entries:
                employee_project_list_per_month_entries.unlink()
            
            employee_list = self.env['employee.list'].search([('employee_code', '=', record.employee_code.id)], limit=1)
            employee_project_list = self.env['employee.project.list'].search([('employee_code', '=', record.employee_code.id), ('project_code', '=', record.project_code.id)])
            project_list = self.env['project.list'].search([('project_code', '=', record.project_code.id)])

        
            deleted = super(ProjectEmployeeAssign, record).unlink()

            if employee_list:
                employee_list._compute_total_projects()
                employee_list._compute_total_earning()
                
            if employee_project_list:
                employee_project_list._compute_hours()
                employee_project_list._compute_costs()
            
            if project_list:
                project_list._compute_hours_costs()

        return deleted

    def write(self, vals):
        result = super(ProjectEmployeeAssign, self).write(vals)
        for record in self:
            employee_list = self.env['employee.list'].search([('employee_code', '=', record.employee_code.id)], limit=1)
            employee_project_list = self.env['employee.project.list'].search([('employee_code', '=', record.employee_code.id), ('project_code', '=', record.project_code.id)])
            project_list = self.env['project.list'].search([('project_code', '=', record.project_code.id)])

            if employee_list:
                employee_list._compute_total_projects()
                employee_list._compute_total_earning()

            if employee_project_list:
                employee_project_list._compute_hours()
                employee_project_list._compute_costs()
            
            if project_list:
                project_list._compute_hours_costs()

        return result

