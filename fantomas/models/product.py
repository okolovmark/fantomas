""" Adding manufacturer and model for product. """


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    """ Add new fields in product model. """

    _inherit = "product.template"

    manufacturer_id = fields.Many2one('product.manufacturer', string='Manufacturer', help='Select manufacturer.')
    model_id = fields.Many2one('product.model', string="Model", domain="[('manufacturer_id', '=', manufacturer_id)]", help='Select model.')

    @api.onchange('manufacturer_id')
    def on_change_manufacturer_id(self):
        """ Сlears the variable. """

        self.model_id = None


class ProductManufacturer(models.Model):
    """ Create new table for product model. """

    _name = "product.manufacturer"

    name = fields.Char(required=True, string="Name")


class ProductModel(models.Model):
    """ Create new table for product model. """

    _name = "product.model"

    name = fields.Char(required=True, string="Name")
    manufacturer_id = fields.Many2one('product.manufacturer', string='Manufacturer', required=True, help='Select manufacturer.')
