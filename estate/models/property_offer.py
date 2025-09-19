from datetime import timedelta
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer Training"
    _order = "price desc"

    _sql_constraints = [('check_price', 'CHECK(price >= 0)',
                         'Offer price needs to be strictly positive'),]
    price = fields.Float()
    status = fields.Selection(
        string = "Offer Status",
        selection = [('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False,
    )
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_deadline', inverse='_inverse_deadline', store=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    def action_accept_offer(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer = record.partner_id.name
            record.property_id.state = 'offer_accepted'


    def action_refuse_offer(self):
        for record in self:
            record.status = 'refused'


    @api.depends('create_date','validity')
    def _compute_deadline(self):
        for offer in self:
            if offer.create_date and offer.validity:
                offer.date_deadline = offer.create_date.date() + timedelta(days=offer.validity)
            else:
                offer.date_deadline = False

    def _inverse_deadline(self):
        for offer in self:
            if offer.create_date and offer.date_deadline:
                delta = offer.date_deadline - offer.create_date.date()
                offer.validity = delta.days

    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')
        amount = vals.get('price')

        if property_id and amount:

            existing_offers = self.search([('property_id', '=', property_id)])

            if any(offer.price > amount for offer in existing_offers):
                raise UserError("You cannot create an offer lower than an existing one")

            current_property = self.env['estate.property'].browse(property_id)
            if current_property.state != 'offer_received':
                current_property.state = 'offer_received'
        return super().create(vals)