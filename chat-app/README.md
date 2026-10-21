# DevHub Realtime Team Chat

A single-page real-time developer chat application designed for deployment to **Cloudflare Pages** on a strict **$0 budget** using **Firebase Realtime Database** and **Anonymous Authentication**.

---

## 1. Cloudflare Pages $0 Deployment Guide

You can deploy this application for free to a custom `*.pages.dev` subdomain in less than 2 minutes. No credit card or paid subscription is required.

### Method A: Direct Upload (Drag-and-Drop — Fastest & No Git Required)

1. **Sign in to Cloudflare:**
   - Go to [dash.cloudflare.com](https://dash.cloudflare.com/) and create a free account or log in.
2. **Navigate to Workers & Pages:**
   - In the left sidebar, click **Workers & Pages** ➔ **Create Application** ➔ select the **Pages** tab.
3. **Upload Assets:**
   - Select **Upload assets**.
   - Enter a Project Name (e.g. `pet-mining-empire-chat` or `devhub-chat`).
   - Click **Create project**.
4. **Drag & Drop the Folder:**
   - Drag and drop the `chat-app` folder (which contains `index.html`) directly into the Cloudflare upload dropzone.
5. **Deploy:**
   - Click **Deploy site**.
   - Your site will instantly be live at `https://<your-project-name>.pages.dev`!

---

### Method B: GitHub Integration (Continuous Deployment)

1. Push this repository to GitHub.
2. In Cloudflare Dashboard, go to **Workers & Pages** ➔ **Create** ➔ **Pages** ➔ **Connect to Git**.
3. Select your repository `Roblox-Studio-AI`.
4. Configure Build Settings:
   - **Framework preset:** `None`
   - **Build command:** *(Leave empty)*
   - **Build output directory:** `chat-app`
5. Click **Save and Deploy**. Cloudflare Pages will automatically rebuild and deploy on every git push for free.

---

## 2. Firebase $0 Backend Setup (Realtime Database & Anonymous Auth)

Firebase's free Spark plan provides 1 GB of storage, 10 GB/month data transfer, and 100 simultaneous Realtime Database connections at $0/month.

### Step 1: Create a Firebase Project
1. Go to the [Firebase Console](https://console.firebase.google.com/) and click **Add project**.
2. Enter a project name (e.g. `pet-mining-empire-chat`).
3. Disable Google Analytics (optional, keeps setup quick) and click **Create project**.

### Step 2: Enable Anonymous Authentication
1. In the Firebase console sidebar, navigate to **Build** ➔ **Authentication**.
2. Click **Get started**.
3. Under the **Sign-in method** tab, click **Anonymous**.
4. Toggle **Enable** to ON and click **Save**.
   *(This gives every developer an instant, secure session without requiring passwords or emails).*

### Step 3: Create Realtime Database
1. In the sidebar, navigate to **Build** ➔ **Realtime Database**.
2. Click **Create Database**.
3. Choose your nearest database location (e.g. `United States (us-central1)`).
4. Select **Start in test mode** and click **Enable**.

### Step 4: Apply Production Security Rules
1. In Realtime Database, click the **Rules** tab.
2. Replace all contents with the following exact JSON rules:

```json
{
  "rules": {
    "rooms": {
      "$roomId": {
        "messages": {
          ".read": true,
          ".write": "auth != null",
          "$messageId": {
            ".validate": "newData.hasChildren(['userId', 'userName', 'text', 'timestamp']) && newData.child('text').isString() && newData.child('text').val().length > 0 && newData.child('text').val().length <= 500"
          }
        }
      }
    }
  }
}
```

3. Click **Publish**.
   - These rules allow any authenticated user (including anonymous developer sessions) to post messages up to 500 characters.
   - They prevent invalid data schemas and eliminate Firebase security warning emails.

### Step 5: Copy Your Web App Credentials
1. Click the **Project Overview** gear icon ⚙️ ➔ **Project settings**.
2. Scroll down to **Your apps** and click the Web icon (`</>`).
3. Enter an app nickname (e.g. `DevChat Web`) and click **Register app**.
4. You will see your `firebaseConfig` object:
   ```javascript
   const firebaseConfig = {
     apiKey: "AIzaSy...",
     authDomain: "your-project.firebaseapp.com",
     databaseURL: "https://your-project-default-rtdb.firebaseio.com",
     projectId: "your-project",
     appId: "1:..."
   };
   ```
5. Open your live Cloudflare Pages chat app, click the **⚙️ Settings** icon in the top right, paste these values, and click **Save & Reconnect**!

---

## 3. Key Application Features

- **Multi-Room Routing:** Join `#general`, `#roblox-dev`, `#ui-design`, or create custom rooms. Share any room instantly using the `?room=roomName` URL parameter.
- **Copy Shareable Link:** One-click button copies the direct room URL for quick sharing in Discord, Slack, or GitHub issues.
- **Synthesized Audio Notifications:** Web Audio API produces clean harmonic chime notifications when team members post (with toggleable mute).
- **Auto-Generated Handles:** Adjective + Noun handles (e.g. `CosmicFalcon_412`, `NeonSamurai_805`) with a 🎲 roll button and custom handle editing.
- **Input Guardrails:** 500-character limit counter with warning colors and auto-expanding textarea.
- **XSS Sanitization:** All text is defensively HTML-escaped with safe clickable link formatting for URLs.
- **Connection Diagnostics:** Live visual badge indicates Realtime Database connection status (`Online`, `Connecting`, `Offline`).
