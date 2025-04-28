# -*- coding: utf-8 -*-

import time
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
import requests
import logging
import base64
from lxml import etree
from lxml.builder import ElementMaker
import xml.etree.ElementTree as ET
import datetime

class AccountMove(models.Model):
    _inherit = "account.move"

    factura_cf = fields.Boolean(string='CF', copy=False, tracking=True)
    fecha_receptionPago = fields.Date(
        string='Fecha de recepcion'
    )

    fecha_pago = fields.Date(
        string='Fecha de pago'
    )

    contraseia_pago = fields.Char (
        string='Contraseña de pago'
    )
    
# 4 1 , exportacion
    def fecha_hora_factura(self, fecha):
        fecha_convertida = datetime.datetime.strptime(str(fecha), '%Y-%m-%d').date().strftime('%Y-%m-%d')
        hora = datetime.datetime.strftime(fields.Datetime.context_timestamp(self, datetime.datetime.now()), "%H:%M:%S")
        fecha_hora_emision = str(fecha_convertida)+'T'+str(hora)
        return fecha_hora_emision


    def verificar_lineas_sin_impuestos(self, lineas):
        linea_sin_impuesto = False
        for linea in lineas:
            if len(linea.tax_ids) == 0:
                linea_sin_impuesto = True

        return linea_sin_impuesto

    def obtener_numero_identificacion(self, partner_id):
        res = super(AccountMove, self).obtener_numero_identificacion(partner_id)
        for factura in self:
            if factura.factura_cf:
                res['id_receptor'] = "CF"
                res['tipo_especial'] = False
        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discounted_product = fields.Float(string='Bonificación', store=True)