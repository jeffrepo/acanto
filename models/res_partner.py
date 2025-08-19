# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_due = fields.Monetary(groups='account.group_account_readonly,account.group_account_invoice,sales_team.group_sale_salesman')
    followup_status = fields.Selection(groups='account.group_account_readonly,account.group_account_invoice,sales_team.group_sale_salesman')
    visitas = fields.Char('Visitas')
    observaciones = fields.Char('Observaciones')