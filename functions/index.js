const functions = require('@google-cloud/functions-framework');
const crypto = require('crypto');
const axios = require('axios');

functions.http('paystackWebhook', async (req, res) => {
    const secret = process.env.PAYSTACK_SECRET_KEY;
    
    // 1. Verify Paystack signature
    const sig = req.headers['x-paystack-signature'];
    if (!sig) {
        return res.status(400).send('Missing signature');
    }

    const hash = crypto.createHmac('sha512', secret).update(JSON.stringify(req.body)).digest('hex');
    
    if (hash !== sig) {
        console.error('Invalid signature');
        return res.status(400).send('Invalid signature');
    }

    const paystackEvent = req.body;

    if (paystackEvent.event === 'charge.success') {
        const data = paystackEvent.data;
        const metadata = data.metadata || {};
        
        let telegramId = metadata.telegram_id;
        let planType = metadata.plan_type;
        
        // Sometimes metadata fields are within custom_fields
        if (!telegramId && metadata.custom_fields) {
            for (const field of metadata.custom_fields) {
                if (field.variable_name === 'telegram_id') telegramId = field.value;
                if (field.variable_name === 'plan_type') planType = field.value;
            }
        }

        const email = data.customer?.email;

        if (!telegramId || !planType) {
            console.error("Missing metadata", data.reference);
            return res.status(200).send('Missing metadata, skipped');
        }

        try {
            // 2. Call Telegram API for invite link
            const telegramToken = process.env.TELEGRAM_BOT_TOKEN;
            const chatId = process.env.TELEGRAM_CHAT_ID;
            const expireDate = Math.floor(Date.now() / 1000) + 604800; // 7 days

            const tgResponse = await axios.post(`https://api.telegram.org/bot${telegramToken}/createChatInviteLink`, {
                chat_id: chatId,
                name: `Invite ${telegramId}`,
                expire_date: expireDate,
                member_limit: 1
            });

            const inviteLink = tgResponse.data.result.invite_link;

            // 3. Send email via Resend
            if (email && inviteLink) {
                const resendApiKey = process.env.RESEND_API_KEY;
                await axios.post('https://api.resend.com/emails', {
                    from: process.env.EMAIL_FROM,
                    to: email,
                    subject: 'Your Premium Telegram Invite',
                    html: `<p>Thank you for subscribing! Join here: <a href="${inviteLink}">${inviteLink}</a></p>`
                }, {
                    headers: { 'Authorization': `Bearer ${resendApiKey}` }
                });
            }

            // 4. Call FastAPI to record payment
            const fastApiUrl = process.env.FASTAPI_BASE_URL || 'https://financebot-production.up.railway.app';
            // Forward the webhook payload to FastAPI's webhook endpoint
            await axios.post(`${fastApiUrl}/webhook/paystack`, paystackEvent, {
                headers: { 'x-paystack-signature': sig } // Forward signature so FastAPI can verify too
            });

            return res.status(200).send('Success');
        } catch (error) {
            console.error("Error processing checkout:", error.response?.data || error.message);
            return res.status(500).send('Internal Server Error');
        }
    }

    return res.status(200).send('Received');
});
