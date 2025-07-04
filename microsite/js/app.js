// GringoOps Microsite JS

document.addEventListener("DOMContentLoaded", () => {
    const upgradeButton = document.getElementById("upgrade-button");
    if (upgradeButton) {
        upgradeButton.addEventListener("click", async () => {
            // In a real app, you would get the user's ID token here
            const idToken = "YOUR_FIREBASE_ID_TOKEN"; // Placeholder

            try {
                const response = await fetch("https://us-central1-chatterfix-ui.cloudfunctions.net/createCheckoutSession", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${idToken}`
                    }
                });

                const session = await response.json();
                window.location.href = session.url;
            } catch (error) {
                console.error("Error creating checkout session:", error);
            }
        });
    }
});
