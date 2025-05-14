from odoo import models, fields, api

class DepartmentMaster(models.Model):
    _name = "department.master"
    _description = "Department Master"

    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    code = fields.Char(required=True, help='Unique Key', index=True)
    name = fields.Char(required=True)
    order = fields.Integer(required=True)
    delete_flag = fields.Boolean(default=False, help='False for available department and vice-versa.')
    description = fields.Text()

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'The department code must be unique.'),
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
