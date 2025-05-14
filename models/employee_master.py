from odoo import models, fields

class EmployeeMaster(models.Model):
    _name = "employee.master"
    _description = "Employee Master"

    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    code = fields.Char(required=True, help='Unique Key', index=True)
    name = fields.Char(required=True)
    department_code = fields.Many2one('department.master', required=True, help='Enter Department Code.', index=True)
    class_code = fields.Many2one('employee.class.master', string='Employee Class Code', required=True, help='Enter Employee Class Code.', index=True)
    delete_flag = fields.Boolean(default=False, help='False for available employee and vice-versa.')
    description = fields.Text()

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'The employee code must be unique.'),
    ]

    def _compute_sequence_no(self):
        all_records = self.search([])
        for index, record in enumerate(all_records, start=1):
            record.no = index

    def _compute_display_name(self):
        for record in self:
            if self.env.context.get('show_name', False):
                    record.display_name = f"{record.name}"
            else:
                    record.display_name = f"{record.code}"

    def create(self, vals):
        record = super(EmployeeMaster, self).create(vals)

        existing_employee = self.env['employee.list'].search([
            ('employee_code', '=', record.id),
        ], limit=1)

        if not existing_employee:
            self.env['employee.list'].create({
                'employee_code': record.id,
            })
                
        return record

    def unlink(self):
        for record in self:
            assignments = self.env['project.employee.assign'].search([
                ('employee_code', '=', record.id)
            ])
            if assignments:
                assignments.unlink()

            list_entries = self.env['employee.list'].search([
                ('employee_code', '=', record.id)
            ])
            if list_entries:
                list_entries.unlink()

        return super(EmployeeMaster, self).unlink()
