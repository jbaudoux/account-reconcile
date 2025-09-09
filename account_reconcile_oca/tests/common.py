from odoo import Command

from odoo.addons.account_reconcile_model_oca.tests.common import (
    TestAccountReconciliationCommon as TestAccountReconciliationModelCommon,
)


class TestAccountReconciliationCommon(TestAccountReconciliationModelCommon):
    @classmethod
    def _setup_context(cls):
        return {**cls.env.context, "_test_account_reconcile_oca": True}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=cls._setup_context())
        # Auto-disable reconciliation model created automatically with
        # generate_account_reconcile_model() to avoid side effects in tests
        cls.invoice_matching_models = cls.env["account.reconcile.model"].search(
            [
                ("rule_type", "=", "invoice_matching"),
                ("auto_reconcile", "=", True),
                ("company_id", "=", cls.company.id),
            ]
        )
        cls.invoice_matching_models.active = False

        cls.acc_bank_stmt_model = cls.env["account.bank.statement"]
        cls.acc_bank_stmt_line_model = cls.env["account.bank.statement.line"]
        cls.bank_journal_usd.suspense_account_id = (
            cls.env.company.account_journal_suspense_account_id
        )
        cls.bank_journal_euro.suspense_account_id = (
            cls.env.company.account_journal_suspense_account_id
        )
        cls.current_assets_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_current"),
                ("company_ids", "in", cls.env.company.id),
            ],
            limit=1,
        )
        cls.current_assets_account.reconcile = True

        cls.rule = cls.env["account.reconcile.model"].create(
            {
                "name": "write-off model",
                "rule_type": "writeoff_button",
                "match_partner": True,
                "match_partner_ids": [],
                "line_ids": [
                    Command.create({"account_id": cls.current_assets_account.id})
                ],
            }
        )
        cls.tax_10 = cls.env["account.tax"].create(
            {
                "name": "tax_10",
                "amount_type": "percent",
                "amount": 10.0,
            }
        )
        # We need to make some fields visible in order to make the tests work
        cls.env["ir.ui.view"].create(
            {
                "name": "DEMO Account bank statement",
                "model": "account.bank.statement.line",
                "inherit_id": cls.env.ref(
                    "account_reconcile_oca.bank_statement_line_form_reconcile_view"
                ).id,
                "arch": """
            <data>
                <field name="manual_reference" position="attributes">
                    <attribute name="invisible">0</attribute>
                </field>
                <field name="manual_delete" position="attributes">
                    <attribute name="invisible">0</attribute>
                </field>
                <field name="partner_id" position="attributes">
                    <attribute name="invisible">0</attribute>
                </field>
            </data>
            """,
            }
        )
