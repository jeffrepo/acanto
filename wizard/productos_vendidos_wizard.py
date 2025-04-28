# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import time
import logging
import datetime
from datetime import datetime

class AcantoProductosVendidosWizard(models.TransientModel):
    _name = 'acanto.productos_vendidos.wizard'

    def _default_cliente(self):
        if len(self.env.context.get('active_ids', [])) > 0:
            oportunidad = self.env['crm.lead'].search([('id','in',self.env.context.get('active_ids'))])
            return oportunidad.partner_id.id
        else:
            return None
            
    fecha_inicio = fields.Date(string="Fecha inicio")
    fecha_fin = fields.Date(string="Fecha fin")
    cliente_id = fields.Many2one("res.partner", string="Cliente", default=_default_cliente)

    def confirm_action(self):
        data_ids = []
        logging.warning(self.cliente_id)
        lineas_factura = self.env['account.move.line'].search([
            ('move_id.invoice_date', '>=', self.fecha_inicio),
            ('move_id.invoice_date', '<=', self.fecha_fin),
            ('move_id.partner_id', '=', self.cliente_id.id),
            ('account_id.account_type', '=', 'income'),
            ('price_subtotal', '>', 0),
        ],order="date ASC")
        logging.warning(lineas_factura)
        if len(lineas_factura) > 0:
            data_ids = lineas_factura.ids
        domain = [("id","in",data_ids)]
        logging.warning(domain)
        return {

            'type': 'ir.actions.act_window',
            'name': 'Productos vendidos',
            'res_model': 'account.move.line',
            'view_id': self.env.ref('acanto.view_acanto_productos_vendidos_move_line_tree').id,
            'view_mode': 'list',
            'domain': domain,
            'target': 'current'
        } 

