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


    @api.depends('order_line.margin', 'amount_untaxed')
    def _compute_margin(self):
        res = super()._compute_margin()
        for order in self:
            order_amount_untax = 0
            for line in order.order_line:
                if line.product_uom_qty > 0:
                    prince_unit_untax = line.price_subtotal / line.product_uom_qty
                    #final_qty = line.product_uom_qty + line.discounted_product
                    #order_amount_untax += (prince_unit_untax * final_qty)
                    order_amount_untax += (line.price_subtotal)
            logging.warning("_compute_margin")
            logging.warning(order_amount_untax)
            order.margin = sum(order.order_line.mapped('margin'))
            order.margin_percent = order_amount_untax and order.margin/order_amount_untax
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin = fields.Float(
        "Margin", groups="base.group_erp_manager")
    margin_percent = fields.Float(
        "Margin (%)", groups="base.group_erp_manager")
    discounted_product = fields.Float(string='Bonificación', store=True)
    ultimo_precio_venta = fields.Float(string="último precio de venta")
    purchase_price = fields.Float(groups="account.group_account_manager")
    margin = fields.Float(groups="account.group_account_manager")
    margin_percent = fields.Float(groups="account.group_account_manager")

    @api.onchange('product_id')
    def _change_product_id(self):
        for linea in self:
            if linea.product_id:
                ultima_venta_id = self.env["sale.order.line"].search([("product_id","=", linea.product_id.id),("state","=","sale"),("order_partner_id","=", linea.order_partner_id.id)], order="create_date desc", limit=1)
                if ultima_venta_id:
                    linea.write({"ultimo_precio_venta": ultima_venta_id.price_unit}) 

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line()
        res["discounted_product"] = self.discounted_product
        return res

    @api.depends('price_subtotal', 'product_uom_qty', 'purchase_price','discounted_product','qty_delivered')
    def _compute_margin(self):
        res = super()._compute_margin()
        for line in self:
            if line.discounted_product > 0:
                line_price_subtotal = line.price_subtotal
                line.margin = line_price_subtotal - (line.purchase_price * line.qty_delivered)
                line.margin_percent = line_price_subtotal and line.margin / line_price_subtotal
            else:
                return res