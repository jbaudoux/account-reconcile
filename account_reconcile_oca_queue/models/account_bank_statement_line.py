# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def _enqueue_auto_reconcile(self, models):
        if not self.company_id.account_auto_reconcile_queue:
            return super()._enqueue_auto_reconcile(models)
        self.with_delay(
            description=self.env._("Auto reconcile %(label)s", label=self.payment_ref)
        )._auto_reconcile(models)
