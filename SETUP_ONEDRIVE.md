# OneDrive Auto-Refresh Setup Guide

This guide wires up the GitHub Actions pipeline that fetches NBA data twice per day
and uploads the CSVs to your OneDrive. Power BI Online then refreshes from OneDrive
with no gateway, no local computer required.

---

## Architecture

```
GitHub Actions (cron: 6am + 6pm ET)
  → runs Python scripts → fetches live NBA stats
  → uploads 4 CSVs to OneDrive folder
      → Power BI Online reads from OneDrive
          → Dashboard auto-refreshes
              → Embed URL stays live on cleardatareport.com
```

---

## Step 1 — Create the OneDrive Folder

1. Go to [onedrive.live.com](https://onedrive.live.com) (or OneDrive for Business)
2. Create a folder: `NBA Dashboard/data`
3. Manually upload the 4 CSVs from `data/raw/` once to initialize the folder:
   - `player_stats.csv`
   - `team_standings.csv`
   - `game_log.csv`
   - `advanced_stats.csv`

---

## Step 2 — Register an Azure AD App (5 minutes)

GitHub Actions needs permission to upload files to your OneDrive.
You'll create a free Azure AD app registration to get credentials.

1. Go to [portal.azure.com](https://portal.azure.com) → **Azure Active Directory** → **App registrations** → **New registration**
2. Name: `NBA Dashboard Uploader`
3. Supported account types: **Accounts in this organizational directory only**
4. Click **Register**

**Copy these values — you'll need them for GitHub Secrets:**
- `Application (client) ID` → this is your `CLIENT_ID`
- `Directory (tenant) ID` → this is your `TENANT_ID`

### Add a Client Secret
5. In your app → **Certificates & secrets** → **New client secret**
6. Description: `github-actions`, Expires: **24 months**
7. Copy the **Value** immediately (shown only once) → this is your `CLIENT_SECRET`

### Grant API Permissions
8. In your app → **API permissions** → **Add a permission** → **Microsoft Graph** → **Application permissions**
9. Search and add: `Files.ReadWrite.All`
10. Click **Grant admin consent** (requires admin — if you're on a personal Microsoft account this is automatic)

---

## Step 3 — Add GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 5 secrets:

| Secret name | Value |
|-------------|-------|
| `TENANT_ID` | Your Azure AD Directory (tenant) ID |
| `CLIENT_ID` | Your Azure AD Application (client) ID |
| `CLIENT_SECRET` | The client secret value you copied |
| `ONEDRIVE_USER` | Your Microsoft 365 email (e.g. `johnd.pereyra@gmail.com` or your work email) |
| `ONEDRIVE_FOLDER_PATH` | `NBA Dashboard/data` |

---

## Step 4 — Connect Power BI Desktop to OneDrive

Power BI reads the CSVs directly from OneDrive via the Web connector.

1. Open `powerbi/pbir nba dashboard/nba_dashboard.pbip` in Power BI Desktop
2. Go to **Transform Data → Manage Parameters**
3. Update `OneDriveFolderURL` to the **direct download base URL** for your OneDrive folder.

### How to get your OneDrive direct URL

The URL format depends on whether you use personal OneDrive or OneDrive for Business:

**Personal OneDrive (onedrive.live.com):**
```
https://onedrive.live.com/download?resid=XXXX&authkey=XXXX&path=/player_stats.csv
```
Get this by right-clicking each CSV in OneDrive → **Share** → **Copy link**, then switch to direct download format.

**OneDrive for Business (SharePoint):**
```
https://yourtenant.sharepoint.com/personal/yourname/_layouts/15/download.aspx?SourceUrl=/personal/yourname/Documents/NBA Dashboard/data/
```

> **Easiest approach:** In OneDrive, right-click `player_stats.csv` → **Embed** or **Share** → get the base URL, then strip the filename. The `OneDriveFolderURL` parameter is that base URL with a trailing slash — the table queries append the filename.

4. Click **Close & Apply** — all 4 tables load from OneDrive
5. Save and **Publish to Power BI Online** (Home → Publish → select your workspace)

---

## Step 5 — Configure Scheduled Refresh in Power BI Online

1. Go to [app.powerbi.com](https://app.powerbi.com) → your workspace → find `nba_dashboard` semantic model
2. Click **⋯ → Settings → Scheduled refresh**
3. Toggle **Keep your data up to date** → On
4. Add refresh times: **6:15 AM** and **6:15 PM** (15min after GitHub Actions runs)
5. Time zone: **Eastern Time**
6. **Save**

> Power BI will re-read the CSVs from OneDrive at these times. Since GitHub Actions uploads fresh data at 6am/6pm, the 15-minute offset ensures the new files are in place before the refresh fires.

---

## Step 6 — Test the Pipeline

Trigger a manual run to verify everything works end-to-end:

1. GitHub repo → **Actions** → **Refresh NBA Data → OneDrive** → **Run workflow**
2. Watch the logs — should show 4 CSV uploads succeeding
3. Check your OneDrive `NBA Dashboard/data` folder — files should be updated
4. In Power BI Online → manually trigger a dataset refresh → verify data loads

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` in Actions | Wrong CLIENT_SECRET or expired | Regenerate secret in Azure portal, update GitHub secret |
| `403 Forbidden` | Missing admin consent on `Files.ReadWrite.All` | Re-grant admin consent in Azure portal |
| `ONEDRIVE_USER not set` | Missing secret | Add `ONEDRIVE_USER` secret with your Microsoft 365 email |
| Power BI refresh fails: `credentials required` | PBI can't auth to OneDrive URL | In PBI Online dataset settings → **Data source credentials** → edit → sign in with your Microsoft account |
| nba_api rate limit / timeout | NBA Stats API blocks | Re-run workflow; script has 1s delays built in |
