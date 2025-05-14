from odoo import models, fields, api

class EmployeeClassMaster(models.Model):
    _name = "employee.class.master"
    _description = "Employee Class Master"

    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    code = fields.Char(required=True, help='Unique Key', index=True)
    name = fields.Char(required=True)
    currency_id = fields.Many2one(
        'res.currency', 
        default=lambda self: self.env['res.currency'].search([('name', '=', 'JPY')], limit=1),
        readonly=True
    )
    unit_price = fields.Monetary(required=True)
    delete_flag = fields.Boolean(default=False, help='False for available employee class and vice-versa.')
    description = fields.Text()

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'The employee class code must be unique.'),
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
