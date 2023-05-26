from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    community_id = fields.Integer('Community Task ID')

    @api.model
    def create(self, vals):
        fsm_project = self.env.ref('industry_fsm.fsm_project', raise_if_not_found=False)
        res = super(ProjectTask, self).create(vals)
        if res and fsm_project and fsm_project.id == vals['project_id']:
            field_service_sync_obj = self.env['field.service.sync'].search([('state','=','connected'),('auto_sync','=',True)])
            for field_service_sync in field_service_sync_obj:
                args = {
                        'name':vals['name'],
                        'project_id':field_service_sync.project_id
                }

                if vals.get('user_ids'):
                    args.update({'user_ids':vals['user_ids']})

                community_id = field_service_sync.process_values('project.task','create',[args])
                res.write({'community_id':community_id})
        return res

    def write(self, vals):
        fsm_project = self.env.ref('industry_fsm.fsm_project', raise_if_not_found=False)
        project_id = vals.get('project_id') or self.project_id.id
        res = super(ProjectTask, self).write(vals)
        if res and fsm_project and self.community_id and project_id and fsm_project.id == project_id:
            field_service_sync_obj = self.env['field.service.sync'].search(
                [('state', '=', 'connected'), ('auto_sync', '=', True)])
            for field_service_sync in field_service_sync_obj:
                arg_vals = {'name': self.name}
                if vals.get('user_ids'):
                    arg_vals.update({'user_ids':vals['user_ids']})
                args = [[self.community_id], arg_vals]
                field_service_sync.process_values('project.task', 'write', args)
        return res
