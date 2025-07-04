const functions = require("firebase-functions");
const admin = require("firebase-admin");
const stripe = require("stripe")("YOUR_STRIPE_SECRET_KEY"); // Replace with your Stripe secret key

admin.initializeApp();

exports.createCheckoutSession = functions.https.onCall(async (data, context) => {
  const uid = context.auth?.uid;
  if (!uid) {
    throw new functions.https.HttpsError("unauthenticated", "User must be authenticated");
  }

  const YOUR_PRICE_ID = "YOUR_STRIPE_PRICE_ID"; // Replace with your real price ID from Stripe

  const session = await stripe.checkout.sessions.create({
    payment_method_types: ["card"],
    mode: "subscription",
    line_items: [
      {
        price: YOUR_PRICE_ID,
        quantity: 1,
      },
    ],
    success_url: "https://chatterfix.ai/success",
    cancel_url: "https://chatterfix.ai/cancel",
    metadata: {
      firebaseUID: uid,
    },
  });

  return {
    id: session.id,
  };
});

exports.handleStripeWebhook = functions.https.onRequest(async (req, res) => {
    const sig = req.headers["stripe-signature"];
    const endpointSecret = "YOUR_STRIPE_WEBHOOK_SECRET"; // Replace with your webhook secret from Stripe
  
    let event;
    try {
      event = stripe.webhooks.constructEvent(req.rawBody, sig, endpointSecret);
    } catch (err) {
      res.status(400).send(`Webhook error: ${err.message}`);
      return;
    }
  
    if (event.type === "checkout.session.completed") {
      const uid = event.data.object.metadata.firebaseUID;
  
      // Upgrade user plan
      await admin.firestore().collection("users").doc(uid).set({
        plan: "team",
        commands_limit: 1000,
      }, { merge: true });
    }
  
    res.sendStatus(200);
  });
