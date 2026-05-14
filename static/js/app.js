// =========================================================================
// GLOBAL PUBLIC WEB CONTROLLERS
// =========================================================================
function toggleMenu() {
    const menu = document.getElementById("menu");
    if (menu) menu.classList.toggle("active");
}

document.addEventListener("DOMContentLoaded", () => {
    const amountInput = document.getElementById("amount");
    const feeText = document.getElementById("fee");
    const totalText = document.getElementById("total");
    const currencySelect = document.querySelector("select[name='currency']");
    const paymentForm = document.querySelector(".payment-form");

    // Dynamic UI Conversion Display Elements Injection
    let ghsSummaryBox = document.getElementById("ghs-summary-box");
    if (!ghsSummaryBox && paymentForm) {
        ghsSummaryBox = document.createElement("div");
        ghsSummaryBox.id = "ghs-summary-box";
        ghsSummaryBox.style.cssText = "background: rgba(0, 255, 204, 0.05); padding: 15px; border-radius: 12px; margin-bottom: 20px; font-size: 14px; border: 1px dashed rgba(0, 255, 204, 0.2); color: #00ffcc; display: none; justify-content: space-between;";
        const feesBox = document.querySelector(".fees-box");
        if (feesBox) feesBox.parentNode.insertBefore(ghsSummaryBox, feesBox.nextSibling);
    }

    let databaseRates = {};

    // Fetch dynamic overrides matrix from backend API channel
    fetch('/api/rates')
        .then(response => response.json())
        .then(data => {
            databaseRates = data;
            calculateFees(); // Init calculation once values map successfully
        })
        .catch(err => console.error("Error fetching live operations rates matrix: ", err));

    function calculateFees() {
        if (!amountInput || !feeText || !totalText) return;

        let amount = parseFloat(amountInput.value) || 0;
        let selectedCurrency = currencySelect ? currencySelect.value : "USD";
        
        // Keeps your strict structural baseline calculation rules: 3% markup cost
        let fee = amount * 0.03;
        let total = amount + fee;

        feeText.innerText = fee.toFixed(2);
        totalText.innerText = total.toFixed(2);

        // Multi-Currency Payout Estimation Logic
        if (amount > 0 && databaseRates[selectedCurrency] && ghsSummaryBox) {
            let marketRate = databaseRates[selectedCurrency];
            let estimatedGhsPayout = amount * marketRate;
            
            ghsSummaryBox.innerHTML = `<div>Estimated Destination Delivery:</div><div style='font-weight: bold;'>¢ ${estimatedGhsPayout.toFixed(2)} GHS</div>`;
            ghsSummaryBox.style.display = "flex";
        } else if (ghsSummaryBox) {
            ghsSummaryBox.style.display = "none";
        }
    }

    if (amountInput) amountInput.addEventListener("input", calculateFees);
    if (currencySelect) currencySelect.addEventListener("change", calculateFees);

    // =========================================================================
    // SECURE INLINE CHECKOUT INITIATION
    // =========================================================================
    function openPaystackPayment() {
        const totalAmount = parseFloat(totalText.innerText) || 0;
        const currency = currencySelect ? currencySelect.value : "USD";
        const senderPhone = document.querySelector("input[name='sender_phone']").value;
        const senderName = document.querySelector("input[name='sender_name']").value;
        const amountInMinorUnits = Math.round(totalAmount * 100);

        const paystackPayload = {
            key: 'pk_live_your_public_key_here', 
            email: 'customer@example.com', 
            amount: amountInMinorUnits,
            currency: currency,
            ref: 'ADG-' + Math.floor((Math.random() * 1000000000) + 1),
            metadata: {
                custom_fields: [
                    { display_name: "Sender Name", variable_name: "sender_name", value: senderName },
                    { display_name: "Sender Phone", variable_name: "sender_phone", value: senderPhone },
                    { display_name: "Recipient Name", variable_name: "recipient_name", value: document.querySelector("input[name='recipient_name']").value },
                    { display_name: "Recipient Phone", variable_name: "recipient_phone", value: document.querySelector("input[name='recipient_phone']").value }
                ]
            },
            callback: function(response) {
                const referenceInput = document.createElement("input");
                referenceInput.type = "hidden";
                referenceInput.name = "paystack_reference";
                referenceInput.value = response.reference;
                paymentForm.appendChild(referenceInput);
                paymentForm.submit();
            },
            onClose: function() {
                alert('Transaction window closed by user.');
            }
        };

        const handler = new PaystackPop();
        handler.newTransaction(paystackPayload);
    }

    if (paymentForm) {
        paymentForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const totalAmount = parseFloat(totalText.innerText) || 0;
            if (totalAmount <= 0) {
                alert("Please enter a valid transfer amount.");
                return;
            }

            if (typeof PaystackPop === 'undefined') {
                const script = document.createElement('script');
                script.src = "paystack.co";
                script.onload = openPaystackPayment;
                script.onerror = () => alert("Network Error: Connection to checkout servers timed out.");
                document.head.appendChild(script);
            } else {
                openPaystackPayment();
            }
        });
    }
});
