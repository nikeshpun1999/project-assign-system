from odoo import models, fields

class ProjectMaster(models.Model):
    _name = "project.master"
    _description = "Project Master"

    no = fields.Integer(string='No.', compute='_compute_sequence_no', store=False)
    code = fields.Char(required=True, help='Unique Key', index=True)
    name = fields.Char(required=True)
    order = fields.Integer(required=True)
    delete_flag = fields.Boolean(default=False, help='False for available project and vice-versa.')
    description = fields.Text()

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'The project code must be unique.'),
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
        record = super(ProjectMaster, self).create(vals)

        existing_project = self.env['project.list'].search([
            ('project_code', '=', record.id),
        ], limit=1)

        if not existing_project:
            self.env['project.list'].create({
                'project_code': record.id,
            })
                
        return record

    def unlink(self):
        for record in self:
            assignments = self.env['project.employee.assign'].search([
                ('project_code', '=', record.id)
            ])
            if assignments:
                assignments.unlink()

            list_entries = self.env['project.list'].search([
                ('project_code', '=', record.id)
            ])
            if list_entries:
                list_entries.unlink()

        return super(ProjectMaster, self).unlink()
