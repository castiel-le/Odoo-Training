from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class Property(models.Model):
    _name = "estate.property"
    _description = "Property Training Table"
    _order = "id desc"

    _sql_constraints = [('check_expected_price','CHECK(expected_price >= 0)',
                         'Expected price needs to be strictly POSITIVE'),
                        ('check_selling_price', 'CHECK(selling_price >= 0)',
                         'Selling price needs to be strictly POSITIVE'),
                        ]

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda self: fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string = 'Orientation',
        selection = [('north', 'North'), ('south', 'South'), ('west', 'West'), ('east', 'East')],
        help = "Separate Garden Orientation",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection = [('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
        default='new',
        copy=False,
        required=True,
        store=True,
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer = fields.Char(copy=False)
    salesperson = fields.Many2one('res.users', default=lambda self: self.env.user)
    tag_id = fields.Many2many("estate.property.tag", string="Property Tag")
    offer_id = fields.One2many('estate.property.offer','property_id',string='Offers')
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    def action_property_sold(self):
        for record in self:
            if record.state != 'cancelled':
                record.state = 'sold'
            else:
                raise UserError("Property is already CANCELLED")


    def action_property_cancel(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'cancelled'
            else:
                raise UserError("Property is already SOLD")

    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_id.price")
    def _compute_best_price(self):
        for record in self:
            all_price = record.offer_id.mapped('price')
            record.best_price = max(all_price) if all_price else 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden is True:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.constrains('selling_price')
    def _check_selling_threshold(self):
        for record in self:
            threshold = record.expected_price * 0.9
            if float_compare(record.selling_price, threshold, precision_digits=2) == -1:
                raise ValidationError('Offer Price must be at least 90% of Expected Price. Please adjust the Offer Price or Expected Price accordingly.')

    @api.ondelete(at_uninstall=False)
    def _check_deletion_allowed(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError((
                    "You cannot delete the property '%s' because its state is '%s'. "
                    "Only properties in 'New' or 'Cancelled' state can be deleted."
                ) % (record.name, record.state))

