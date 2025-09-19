from odoo import fields, models, api

class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type Training"
    _order = "name"

    _sql_constraints = [('check_unique_type','UNIQUE(name)',
                         'Property Type needs to be UNIQUE.')]

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')
    sequence = fields.Integer('Sequence', default=1)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count', store=True)

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)