# Frequency Table Generator (Web App)

A small Flask web app that lets anyone — no coding required — upload a Stata
(`.dta`) file, choose a few options, and download a formatted Excel workbook
of frequency tables (weighted or unweighted, one sheet per variable).

This replaces the Colab notebook version with a proper web app: users never
see or touch code.

---

## 1. How it works

```
Browser                         Flask server (this app)
--------                        ------------------------
1. Upload .dta file    ------->  reads file, shows variable list
2. Choose options       ------->  runs analysis, builds Excel file
3. Click "Download"     <-------  serves Frequency_Tables.xlsx
```

Each visitor gets their own temporary folder under `uploads/`, which is
automatically deleted after 1 hour.

---

## 2. Run it locally (to test before deploying)

You'll need Python 3.10+ installed.

```bash
# 1. Clone your repo (after you've pushed it to GitHub — see Section 4)
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## 3. Project structure

```
.
├── app.py              # Flask routes (upload, options, generate, download)
├── core.py             # All the data logic (no Flask code) — safe to unit test
├── templates/          # HTML pages (Bootstrap-based, no build step needed)
│   ├── base.html
│   ├── index.html
│   ├── options.html
│   ├── result.html
│   └── error.html
├── uploads/             # Temporary per-user files (auto-cleaned, git-ignored)
├── requirements.txt     # Python dependencies
├── Procfile             # Tells hosting platforms how to start the app
└── runtime.txt           # Python version hint for some hosts
```

**If you (or a non-technical teammate) ever need to tweak something:**
- Wording/labels on the pages → edit files in `templates/`
- Analysis logic (e.g. what counts as an "ID variable") → edit `core.py`
- Routes/URLs/upload limits → edit `app.py`

You do **not** need to touch `core.py` to change how the app looks, and you
do **not** need to touch the HTML to change the analysis logic. They're kept
separate on purpose.

---

## 4. Put it on GitHub

GitHub hosts your *code*, not a running server — for that you'll deploy to a
free host in Section 5, which pulls directly from this GitHub repo.

```bash
cd <your-project-folder>
git init
git add .
git commit -m "Initial commit: frequency table generator web app"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

(If you don't have a GitHub repo yet: go to github.com → **New repository** →
give it a name → **do not** initialize with a README (you already have one) →
copy the commands GitHub shows you.)

---

## 5. Deploy it live (pick ONE option)

### Option A — Render.com (recommended: free tier, simplest)

1. Go to https://render.com and sign up (you can sign in with GitHub).
2. Click **New → Web Service**.
3. Connect your GitHub account and select this repository.
4. Render will detect it's a Python app. Fill in:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Under **Environment**, add a variable:
   - `SECRET_KEY` → any random string (e.g. `mySuperSecret123!`)
6. Click **Create Web Service**. Render will build and deploy automatically.
7. After a couple of minutes you'll get a live URL like
   `https://your-app-name.onrender.com` — share that with your users.

Every time you push new commits to GitHub, Render automatically redeploys.

> Free tier note: the app "sleeps" after inactivity and takes ~30-60 seconds
> to wake up on the next visit. Fine for occasional/internal use; upgrade to
> a paid plan if you need it always-on.

### Option B — Railway.app (also simple, free trial credit)

1. Go to https://railway.app and sign in with GitHub.
2. **New Project → Deploy from GitHub repo** → select this repo.
3. Railway auto-detects the `Procfile` and deploys.
4. Add an environment variable `SECRET_KEY` under the **Variables** tab.
5. Once deployed, click **Generate Domain** to get a public URL.

### Option C — PythonAnywhere (good if Render/Railway are blocked at your org)

1. Go to https://www.pythonanywhere.com and create a free account.
2. Open a **Bash console** and run:
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   pip install --user -r requirements.txt
   ```
3. Go to the **Web** tab → **Add a new web app** → choose **Flask** → point
   it at `app.py` in your cloned repo folder.
4. Set the `SECRET_KEY` environment variable in the **Web** tab's WSGI
   configuration file.
5. Click **Reload** — your app is live at `https://<yourusername>.pythonanywhere.com`.

---

## 6. Environment variables (used in production)

| Variable        | Purpose                                      | Default (local dev)     |
|------------------|-----------------------------------------------|--------------------------|
| `SECRET_KEY`     | Signs Flask session cookies — set a real value in production | `dev-secret-key-change-me` |
| `MAX_UPLOAD_MB`  | Max allowed upload size in MB                | `300`                    |
| `PORT`           | Port Flask listens on (most hosts set this automatically) | `5000` |
| `FLASK_DEBUG`    | Set to `false` in production                 | `true`                   |

Set `FLASK_DEBUG=false` in your hosting platform's environment variables once
deployed — debug mode should never be on in production.

---

## 7. Updating the app after deployment

Because deployment is connected to your GitHub repo, updating is simple:

```bash
git add .
git commit -m "Describe your change"
git push
```

Render/Railway will automatically rebuild and redeploy within a minute or two.
On PythonAnywhere, you'll need to `git pull` in the Bash console and click
**Reload** on the Web tab.

---

## 8. Limitations / things to keep in mind

- Free hosting tiers have limited memory — very large `.dta` files (100k+
  rows or 1000+ variables) may be slow or hit memory limits. If that becomes
  an issue, upgrade to a paid instance size.
- Uploaded files are stored temporarily on the server's disk and deleted
  after 1 hour (see `FILE_RETENTION_SECONDS` in `app.py`). Don't rely on this
  as long-term storage.
- This app doesn't have user accounts/authentication. If you need to restrict
  who can access it, most hosts (Render, Railway) support adding basic auth
  or an access password at the platform level — ask if you'd like help
  setting that up.
