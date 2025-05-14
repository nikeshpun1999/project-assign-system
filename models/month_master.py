from odoo import models, fields, api

class MonthMaster(models.Model):
    _name = "month.master"
    _description = "Month Master"
    _rec_name = 'month'

    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    month = fields.Integer(required=True, help='Unique Key', index=True)
    order = fields.Integer(required=True, help='Unique Order')

    _sql_constraints = [
        ('unique_month', 'UNIQUE(month)', 'The month must be unique.'),
    ]

    def _compute_sequence_no(self):
        all_records = self.search([])
        for index, record in enumerate(all_records, start=1):
            record.no = index

    def unlink(self):
        for record in self:
            assignments = self.env['project.employee.assign'].search([
                ('month', '=', record.id)
            ])
            if assignments:
                assignments.unlink()

        return super(MonthMaster, self).unlink()

    def init(self):
        if not self.env['month.master'].search([]):
            month_data = [
                {'month': 4, 'order': 1},  # April
                {'month': 5, 'order': 2},  # May
                {'month': 6, 'order': 3},  # June
                {'month': 7, 'order': 4},  # July
                {'month': 8, 'order': 5},  # August
                {'month': 9, 'order': 6},  # September
                {'month': 10, 'order': 7}, # October
                {'month': 11, 'order': 8}, # November
                {'month': 12, 'order': 9}, # December
                {'month': 1, 'order': 10}, # January
                {'month': 2, 'order': 11}, # February
                {'month': 3, 'order': 12}  # March
            ]
            
            for data in month_data:
                self.env['month.master'].create(data)
