from odoo import models, fields, api
from odoo.exceptions import ValidationError

class YearMaster(models.Model):
    _name = "year.master"
    _description = "Year Master"
    _rec_name = 'year'

    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    year = fields.Char(required=True, help='Unique Key', index=True)
    order = fields.Integer(required=True)
    default_flag = fields.Boolean(default=False, help='If true is set, this year is selected by default.')
    delete_flag = fields.Boolean(default=False, help='False for active year and vice-versa.')

    _sql_constraints = [
        ('unique_year', 'UNIQUE(year)', 'The year must be unique.'),
    ]

    def _compute_sequence_no(self):
        all_records = self.search([])
        for index, record in enumerate(all_records, start=1):
            record.no = index

    @api.constrains('default_flag')
    def _check_only_one_default_year(self):
        if self.default_flag:
            existing_default = self.search([('default_flag', '=', True), ('id', '!=', self.id)])
            if existing_default:
                raise ValidationError("There can only be one default year.")

    def unlink(self):
        for record in self:
            assignments = self.env['project.employee.assign'].search([
                ('year', '=', record.id)
            ])
            if assignments:
                assignments.unlink()

        return super(YearMaster, self).unlink()
