# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.addons.num_to_words.models.numero_letras import numero_a_letras, numero_a_moneda

class ReportMetodoPago(models.AbstractModel):
    _name = 'report.acanto.metodo_pago_report'

    def a_letras(self,monto):
            letras = numero_a_moneda(monto)
            return letras

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'account.payment',
            'docs': docs,
            'a_letras': self.a_letras,

        }
