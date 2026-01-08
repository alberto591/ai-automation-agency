"""Stripe Connect adapter for multi-agent payment splits."""

from typing import Any

import stripe

from config.settings import settings
from domain.ports import PaymentPort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class StripeConnectAdapter(PaymentPort):
    """Adapter for Stripe Connect Express accounts and payment splits."""

    def __init__(self) -> None:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.platform_fee_percent = 0.15  # 15% platform fee

    def create_connected_account(self, agent_email: str, agent_name: str) -> dict[str, Any]:
        """Create Express account for agent.

        Args:
            agent_email: Agent's email address
            agent_name: Agent's display name

        Returns:
            Dict with account_id and onboarding_url
        """
        try:
            account = stripe.Account.create(
                type="express",
                country="IT",
                email=agent_email,
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
                business_type="individual",
                business_profile={
                    "name": agent_name,
                    "mcc": "6531",  # Real estate agents
                },
            )

            # Create account link for onboarding
            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url=f"{settings.BASE_URL}/agents/onboard/refresh",
                return_url=f"{settings.BASE_URL}/agents/onboard/complete",
                type="account_onboarding",
            )

            logger.info(
                "STRIPE_ACCOUNT_CREATED",
                context={"account_id": account.id, "email": agent_email},
            )

            return {
                "account_id": account.id,
                "onboarding_url": account_link.url,
            }

        except stripe.error.StripeError as e:
            logger.error("STRIPE_ACCOUNT_CREATION_FAILED", context={"error": str(e)})
            raise

    def create_payment_with_fee(
        self,
        amount_cents: int,
        currency: str,
        agent_account_id: str,
        description: str,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create payment with platform fee split.

        Args:
            amount_cents: Total amount in cents
            currency: Currency code (e.g., 'eur')
            agent_account_id: Stripe Connect account ID
            description: Payment description
            metadata: Optional metadata dict

        Returns:
            PaymentIntent details
        """
        application_fee = int(amount_cents * self.platform_fee_percent)

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                description=description,
                application_fee_amount=application_fee,
                transfer_data={"destination": agent_account_id},
                on_behalf_of=agent_account_id,
                metadata=metadata or {},
            )

            logger.info(
                "PAYMENT_INTENT_CREATED",
                context={
                    "payment_id": payment_intent.id,
                    "amount": amount_cents,
                    "fee": application_fee,
                },
            )

            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount_cents,
                "application_fee": application_fee,
                "status": payment_intent.status,
            }

        except stripe.error.StripeError as e:
            logger.error("PAYMENT_CREATION_FAILED", context={"error": str(e)})
            raise

    def get_agent_dashboard_link(self, account_id: str) -> str:
        """Generate Express dashboard login link.

        Args:
            account_id: Stripe Connect account ID

        Returns:
            Dashboard URL
        """
        try:
            login_link = stripe.Account.create_login_link(account_id)
            return str(login_link.url)
        except stripe.error.StripeError as e:
            logger.error("DASHBOARD_LINK_FAILED", context={"error": str(e)})
            raise

    def get_account_status(self, account_id: str) -> dict[str, Any]:
        """Check account verification status.

        Args:
            account_id: Stripe Connect account ID

        Returns:
            Account status details
        """
        try:
            account = stripe.Account.retrieve(account_id)
            return {
                "account_id": account.id,
                "charges_enabled": account.charges_enabled,
                "payouts_enabled": account.payouts_enabled,
                "details_submitted": account.details_submitted,
                "requirements": account.requirements,
            }
        except stripe.error.StripeError as e:
            logger.error("ACCOUNT_STATUS_FAILED", context={"error": str(e)})
            raise

    def create_payment_link(
        self,
        amount_cents: int,
        currency: str,
        description: str,
        agent_account_id: str | None = None,
    ) -> str:
        """Create a shareable payment link.

        Args:
            amount_cents: Amount in cents
            currency: Currency code
            description: Product/service description
            agent_account_id: Optional agent for split

        Returns:
            Payment link URL
        """
        try:
            # Create a price for the payment link
            price = stripe.Price.create(
                unit_amount=amount_cents,
                currency=currency,
                product_data={"name": description},
            )

            link_params: dict[str, Any] = {
                "line_items": [{"price": price.id, "quantity": 1}],
            }

            if agent_account_id:
                application_fee = int(amount_cents * self.platform_fee_percent)
                link_params["transfer_data"] = {"destination": agent_account_id}
                link_params["application_fee_amount"] = application_fee

            payment_link = stripe.PaymentLink.create(**link_params)

            logger.info(
                "PAYMENT_LINK_CREATED",
                context={"link_id": payment_link.id, "amount": amount_cents},
            )

            return str(payment_link.url)

        except stripe.error.StripeError as e:
            logger.error("PAYMENT_LINK_FAILED", context={"error": str(e)})
            raise
