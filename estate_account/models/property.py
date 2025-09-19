from odoo import models, Command
from odoo.exceptions import UserError

class Property(models.Model):
    _inherit = 'estate.property'

    def action_property_sold(self):

        res = super().action_property_sold()

        for property in self:
            if not property.offer_id.partner_id.id:
                raise UserError("No buyer for '%s', invoice creation failed", property.name)

            commission_amount = property.selling_price * 0.06
            admin_fee = 100.0

            invoice_vals = {
                'partner_id': property.offer_id.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': [
                    Command.create({
                        'name': "Commission",
                        'quantity': 1,
                        'price_unit': commission_amount,
                    }),
                    Command.create({
                        'name': "Admin Fee",
                        'quantity': 1,
                        'price_unit': admin_fee
                    })
                ]
            }

            invoice = self.env['account.move'].create(invoice_vals)
            print("Invoice '%s' created for '%s'", invoice.name, property.name)

        return res