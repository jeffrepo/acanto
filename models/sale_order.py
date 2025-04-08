from odoo import fields, models,api
import logging

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contacto = fields.Char(compute ="_compute_contacto")
    partner_id = fields.Many2one(required=False)
    partner_invoice_id = fields.Many2one(required=False)
    partner_shipping_id= fields.Many2one(required=False)
    margin = fields.Monetary("Margin", groups="base.group_erp_manager")
    margin_percent = fields.Float("Margin (%)", groups="base.group_erp_manager")

    @api.depends('date_order')
    def _compute_contacto(self):
        for record in self:
            record.contacto = record.opportunity_id.contact_name


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin = fields.Float(
        "Margin", groups="base.group_erp_manager")
    margin_percent = fields.Float(
        "Margin (%)", groups="base.group_erp_manager")
    discounted_product = fields.Float(string='Discounted Product', store=True)


    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line()
        res["discounted_product"] = self.discounted_product
        return res
