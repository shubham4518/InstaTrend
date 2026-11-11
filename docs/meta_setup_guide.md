# Meta & Telegram Setup Guide for TrendBharat

This guide provides step-by-step instructions to obtain the four required credentials for automated Instagram Reel publishing and Telegram alerting:
1. `INSTAGRAM_USER_ID`
2. `INSTAGRAM_ACCESS_TOKEN` (60-day long-lived token)
3. `TELEGRAM_BOT_TOKEN`
4. `TELEGRAM_CHAT_ID`

---

## Part 1: Instagram & Meta Developer Setup

### Step 1.1: Switch Instagram Account to Professional (Creator or Business)
1. Open the **Instagram** app on your phone.
2. Go to your profile -> Tap the hamburger menu (☰) in the top-right -> **Settings and privacy**.
3. Scroll to **For professionals** -> Tap **Account type and tools** -> **Switch to professional account**.
4. Select **Creator** (or **Business**) and complete the on-screen steps.
   > **Important:** Meta Graph API strictly requires a Professional account; personal accounts cannot publish through the API.

---

### Step 1.2: Create a Meta Developer App
1. On your desktop browser, navigate to [developers.facebook.com](https://developers.facebook.com).
2. Log in with your Facebook account and complete registration if you are a first-time developer.
3. Click **My Apps** (top-right) -> **Create App**.
4. When prompted for use case / app type, select **Other** -> Next -> Select **Business** -> Next.
5. Enter an **App name** (e.g. `TrendBharat`) and your contact email -> Click **Create app**.

---

### Step 1.3: Add Instagram API with Instagram Login
1. On your App Dashboard, scroll to **Add products to your app**.
2. Find **Instagram API with Instagram Login** (or **Instagram**) and click **Set Up**.
3. In the left navigation menu, expand **Instagram API with Instagram Login** -> Click **API Setup with Instagram Login**.
4. Scroll to **User Token Generator** -> Click **Add or Remove Instagram Testers**.
5. You will be redirected to the **Roles** tab -> In the **Instagram Testers** section, click **Add Instagram Testers**.
6. Type your Instagram handle and send the invite.
7. **Accept the invite on your phone:**
   * Open the Instagram app -> Profile -> Settings and privacy.
   * Tap **Creator tools and controls** (or **Business tools and controls**) -> **Tester Invitations**.
   * Accept the invitation from your Meta App.

---

### Step 1.4: Generate Short-Lived Token & Get App Secret
1. Return to [developers.facebook.com](https://developers.facebook.com) -> Open your app -> **Instagram API with Instagram Login** -> **API Setup with Instagram Login**.
2. Under **User Token Generator**, your accepted Instagram account will now be listed.
3. Click **Generate Token**.
4. Log into Instagram when prompted and grant the permissions:
   * `instagram_business_basic`
   * `instagram_business_content_publish`
5. Copy the generated **Short-Lived User Access Token**.
6. To get your **App Secret**:
   * In the left sidebar, click **App settings** -> **Basic**.
   * Under **App Secret**, click **Show** and copy the secret string.

---

### Step 1.5: Run the Token Exchange Script
In your terminal, run:

```powershell
Set-Location -Path "D:\Workspace\Instaposts"
.\.venv\Scripts\python scripts/exchange_token.py
```

The script will prompt you for:
* **Short-Lived Token** (from Step 1.4)
* **App Secret** (from Step 1.4)

It will exchange the token for a **60-day long-lived token**, fetch your `INSTAGRAM_USER_ID`, and automatically save them into `.env`.

---

## Part 2: Telegram Bot Setup

### Step 2.1: Create Your Alert Bot
1. Open the Telegram app on your phone or desktop.
2. In the search bar, search for `@BotFather` (verified bot with blue checkmark).
3. Send `/start` then `/newbot`.
4. Choose a display name (e.g. `TrendBharat Alerts`).
5. Choose a username ending in `bot` (e.g. `trendbharat_alert_bot`).
6. BotFather will reply with your **HTTP API Token**:
   * Example: `7123456789:AAHqweRtyuIopAsdfGhjklZxcvBnm12345`
   * This is your `TELEGRAM_BOT_TOKEN`.

---

### Step 2.2: Get Your Personal Chat ID
1. Search for your new bot on Telegram by its username and click **Start** (or send any text message like `"hello"`).
2. In your desktop browser, open this URL (replace `<YOUR_BOT_TOKEN>` with your real token):
   ```text
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Look for the `"chat":{"id": 123456789}` in the JSON response.
4. That numeric number (e.g. `123456789`) is your `TELEGRAM_CHAT_ID`.

---

### Step 2.3: Test Telegram Connection
In your terminal, run:

```powershell
Set-Location -Path "D:\Workspace\Instaposts"
.\.venv\Scripts\python scripts/test_telegram.py
```

The script will prompt for your token and chat ID, send a test Markdown notification to your phone, and save them into `.env`.

