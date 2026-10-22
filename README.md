# 🛡️ BillBuddy — Smart Warranty Manager & Cloud Invoice Vault

> **BillBuddy** helps consumers store product invoices in the cloud, track warranty expiry dates automatically, and never lose money on missed warranty claims.

---

## ✨ Features Implemented (क्या-क्या बनाया गया है)

1. **🌟 Beautiful Landing / Home Page (फ्रंटएंड होम पेज)**:
   - **Hero Section**: High-impact headlines, "Never lose a bill or warranty again", Google Sign-In CTA, and live preview cards.
   - **Why BillBuddy? (Problem vs. Solution)**: Contrast between old paper receipts (faded, lost, missed claims) and BillBuddy's cloud-secured vault.
   - **Core Features**: 6 feature cards detailing automatic expiry countdowns, Supabase cloud storage, Firebase Google Auth, and gadget expense analytics.
   - **3-Step Workflow**: Visual guide showing how simple it is to track warranties.
   - **Interactive Live Warranty Calculator**: Test purchase date and duration with real-time status badges (*Active*, *Expiring Soon*, *Expired*).
   - **Smooth Navigation**: One-click transition between Landing Page, Google Sign-in, and the Dashboard.

2. **🔐 Firebase Google Sign-In (फ़ायरबेस गूगल लॉगिन)**:
   - Replaced old demo email/password auth with **Firebase Google Authentication**.
   - One-click Google Sign-In with official Google button & popup flow.
   - User profile with Google avatar photo, name, and email displayed in sidebar and topbar.
   - Instant Demo test mode included for quick preview without blocking.

3. **☁️ Supabase Database & File Storage (सुपाबेस डेटाबेस और फ़ाइल स्टोरेज)**:
   - **Supabase PostgreSQL**: Table `products` stores all registered devices, purchase dates, warranty months, prices, categories, and bill links.
   - **Supabase Storage**: Bucket `bills` securely stores uploaded PDF invoices and receipt photos (JPG, PNG, WEBP up to 10 MB).
   - Direct clickable **"📄 View Bill"** link on product cards to open invoices stored in Supabase.
   - Pre-written SQL migration script: [`backend/schema.sql`](file:///c:/Users/Sachin%20Prajapati/Downloads/BillBuddy%20swanandi/BillBuddy/backend/schema.sql).

4. **⚡ Python FastAPI Backend (फास्ट-एपीआई बैकएंड)**:
   - **`backend/main.py`**: FastAPI app with CORS middleware, health check, and static serving.
   - **`backend/routers/products.py`**: Full CRUD (Create, Read with filters/search, Update, Delete) + Expiry and statistics calculation.
   - **`backend/routers/files.py`**: File upload handler connected to Supabase Storage with local fallback.
   - **`backend/routers/user.py`**: Current user profile and Supabase/Firebase connection status.
   - **`backend/auth.py`**: Firebase ID token verification dependency.
   - Interactive Swagger API Documentation available at `http://localhost:8000/docs`.

---

## 📁 Project Structure (प्रोजेक्ट डायरेक्टरी)

```text
BillBuddy/
├── frontend/
│   ├── index.html               # Complete Frontend (Landing Page + Google Login + Dashboard)
│   ├── .env                     # Frontend environment variables (Firebase & API URL)
│   └── .env.example             # Frontend template
├── run.py                       # Easy Python server launcher
├── README.md                    # Documentation & setup guide
├── .env                         # Workspace root environment variables
└── backend/
    ├── main.py                  # FastAPI app entrypoint
    ├── config.py                # Environment configuration
    ├── database.py              # Supabase Client integration
    ├── auth.py                  # Firebase ID Token verification
    ├── models.py                # Pydantic data schemas
    ├── schema.sql               # Ready-to-run Supabase SQL script
    ├── requirements.txt         # Python dependencies
    ├── .env                     # Backend local credentials (Supabase & Firebase)
    ├── .env.example             # Template environment variables
    └── routers/
        ├── products.py          # Product CRUD & warranty calculation
        ├── files.py             # Supabase storage file upload
        └── user.py              # User profile & system health
```

---

## 🚀 Quick Start Guide (शुरू कैसे करें)

### Step 1: Install Python Dependencies (डिपेंडेंसी इनस्टॉल करें)

Open PowerShell / Terminal in the project folder:
```powershell
pip install -r backend/requirements.txt
```

---

### Step 2: Supabase Setup (सुपाबेस सेटअप)

1. Go to [Supabase](https://supabase.com) and create a free project.
2. Open the **SQL Editor** in your Supabase Dashboard.
3. Open [`backend/schema.sql`](file:///c:/Users/Sachin%20Prajapati/Downloads/BillBuddy%20swanandi/BillBuddy/backend/schema.sql), copy its contents, paste it into the Supabase SQL Editor, and click **Run**.
   *(This creates the `products` table, indexes, and sets up the `bills` storage bucket with public read policies).*
4. In Supabase Dashboard, go to **Project Settings** -> **API**:
   - Copy **Project URL**
   - Copy **anon / public key** (or `service_role` key)
5. Paste them into [`backend/.env`](file:///c:/Users/Sachin%20Prajapati/Downloads/BillBuddy%20swanandi/BillBuddy/backend/.env):
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-anon-or-service-role-key
   SUPABASE_STORAGE_BUCKET=bills
   ```

---

### Step 3: Firebase Google Auth Setup (फ़ायरबेस गूगल लॉगिन सेटअप)

1. Go to [Firebase Console](https://console.firebase.google.com) and create a project (e.g. `BillBuddy`).
2. Go to **Authentication** -> **Sign-in method** -> Enable **Google**.
3. Go to **Project Settings** -> Under *Your apps*, click the **Web icon `</>`** to register a web app.
4. Copy the credentials into your `.env` (or `backend/.env`) file:
   ```env
   FIREBASE_API_KEY=AIzaSy...
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=1234567890
   FIREBASE_APP_ID=1:1234567890:web:...
   ```
   *The frontend ([`frontend/index.html`](file:///c:/Users/Sachin%20Prajapati/Downloads/BillBuddy%20swanandi/BillBuddy/frontend/index.html)) automatically loads these settings dynamically from `frontend/.env` or the backend API `/api/config/firebase`!*

   *(Note: BillBuddy also includes an instant 1-click **"⚡ Test with Demo Account"** button so you can test the application right away even before configuring Firebase!)*

---

### Step 4: Run the Backend & Web App (सर्वर चलाएं)

Run the Python server using:
```powershell
python run.py
```
Or with uvicorn directly:
```powershell
uvicorn backend.main:app --reload --port 8000
```

Now open your browser:
- 🌐 **Web App & Landing Page**: [http://localhost:8000](http://localhost:8000) (or double click [`frontend/index.html`](file:///c:/Users/Sachin%20Prajapati/Downloads/BillBuddy%20swanandi/BillBuddy/frontend/index.html))
- 📖 **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📊 **Health Check Endpoint**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
