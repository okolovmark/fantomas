from odoo import api, fields, models


class CreateProductTemplateWizard(models.TransientModel):
    _name = 'create.product.template.wizard'

    product_variant_ids = fields.One2many(
        'product.product', 'product_tmpl_id', 'Products', required=True)

    def _get_default_category_id(self):
        if self._context.get('categ_id') or self._context.get('default_categ_id'):
            return self._context.get('categ_id') or self._context.get('default_categ_id')
        category = self.env.ref(
            'product.product_category_all', raise_if_not_found=False)
        if not category:
            category = self.env['product.category'].search([], limit=1)
        if category:
            return category.id
        else:
            err_msg = _(
                'You must define at least one product category in order to be able to create products.')
            redir_msg = _('Go to Internal Categories')
            raise RedirectWarning(err_msg, self.env.ref(
                'product.product_category_action_form').id, redir_msg)

    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.default_code = template.product_variant_ids.default_code
        for template in (self - unique_variants):
            template.default_code = ''

    @api.one
    def _set_default_code(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.default_code = self.default_code

    def _get_default_uom_id(self):
        return self.env["product.uom"].search([], limit=1, order='id').id

    show_step_one = fields.Boolean(default=True)
    show_step_two = fields.Boolean(default=False)
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type', default='consu', required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')
    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id,
        required=True, help="Select category for the current product")
    uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure',
        default=_get_default_uom_id, required=True,
        help="Default Unit of Measure used for all stock operation.")
    uom_po_id = fields.Many2one(
        'product.uom', 'Purchase Unit of Measure',
        default=_get_default_uom_id, required=True,
        help="Default Unit of Measure used for purchase orders. It must be in the same category than the default unit of measure.")
    sale_ok = fields.Boolean(
        'Can be Sold', default=True,
        help="Specify if the product can be selected in a sales order line.")
    purchase_ok = fields.Boolean('Can be Purchased', default=True)
    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',
        inverse='_set_default_code', store=True)
    manufacturer_id = fields.Many2one(
        'product.manufacturer', string='Manufacturer', help='Select manufacturer.', required=True)
    model_id = fields.Many2one('product.model', string="Model",
                               domain="[('manufacturer_id', '=', manufacturer_id)]", help='Select model.')
    name = fields.Char('Name', required=True, default="")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of the product. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved, "
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")

    @api.onchange('manufacturer_id')
    def on_change_manufacturer_id(self):
        """ Сlears the variable. """

        self.model_id = None

    @api.onchange('manufacturer_id', 'model_id')
    def onchange_name(self):
        self.name = f"{self.manufacturer_id.name if self.manufacturer_id else ''} {self.model_id.name if self.model_id else ''}"

    @api.multi
    def accept_step_one(self):
        self.name = f"{self.manufacturer_id.name if self.manufacturer_id else ''} {self.model_id.name if self.model_id else ''}"
        self.show_step_one, self.show_step_two = self.show_step_two, self.show_step_one

        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def back(self):
        self.name = f"{self.manufacturer_id.name if self.manufacturer_id else ''} {self.model_id.name if self.model_id else ''}"
        self.show_step_one, self.show_step_two = self.show_step_two, self.show_step_one

        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def create_product(self):
        self.name = f"{self.manufacturer_id.name if self.manufacturer_id else ''} {self.model_id.name if self.model_id else ''}"
        vals = {
            'type': self.type,
            'sale_ok': self.sale_ok,
            'purchase_ok': self.purchase_ok,
            'default_code': self.default_code,
            'manufacturer_id': self.manufacturer_id.id,
            'model_id': self.model_id.id,
            'name': self.name,
            'image_medium': self.image_medium,
            'uom_id': self.uom_id.id,
            'uom_po_id': self.uom_po_id.id,
            'categ_id': self.categ_id.id
        }
        product_template_id = self.env['product.template'].create(vals)
