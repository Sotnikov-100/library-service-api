from django.test import TestCase, RequestFactory
from unittest.mock import patch
from payments.webhooks import stripe_webhook
from django.conf import settings


class WebhooksTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        settings.STRIPE_WEBHOOK_SECRET = "test_secret"

    @patch("payments.webhooks.handle_checkout_session")
    def test_stripe_webhook_missing_signature(self, mock_handler):
        request = self.factory.post(
            "/webhook/", data='{"test": "data"}', content_type="application/json"
        )
        response = stripe_webhook(request)
        self.assertEqual(response.status_code, 400)

    @patch("stripe.Webhook.construct_event")
    @patch("payments.webhooks.handle_checkout_session")
    def test_stripe_webhook_valid(self, mock_handler, mock_construct):
        mock_session = type(
            "obj",
            (object,),
            {
                "id": "test_id",
                "payment_status": "paid",
                "url": "http://test.com",
                "amount_total": 1000,
                "metadata": {"payment_id": "1"},
            },
        )

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": mock_session},
        }

        request = self.factory.post(
            "/webhook/",
            data='{"test": "data"}',
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        response = stripe_webhook(request)
        self.assertEqual(response.status_code, 200)
        mock_handler.assert_called_once_with(mock_session)
