# GCP setup steps (what we did)

Project: **My First Project** (`project-5a8ec104-80bd-4f95-a1e`)

## 1) Verify Places API is enabled
- Google Cloud Console → APIs & Services → Library
- Search: **Places API (New)**
- Confirmed it shows **API Enabled** (`places.googleapis.com`)

## 2) Fix 403 caused by IP restriction (IPv6)
We saw `PERMISSION_DENIED` because requests originated from an IPv6 address, while the key was only restricted to IPv4.

We added both:
- IPv4: `104.241.54.210`
- IPv6: `2605:ad80:38:196:2829:9b20:a0aa:a494`

## 3) Create a dedicated key restricted to Places API (New)
- APIs & Services → Credentials → Create credentials → API key
- Edit the new key:
  - Application restrictions: **IP addresses**
    - add IPv4 + IPv6 above
  - API restrictions: **Restrict key** → select **Places API (New)** only
- Save

## 4) Set your local env var (don’t commit)
Set this on your machine (User env recommended):

```powershell
setx OPENCLAW_GOOGLE_PLACES_API_KEY "<PASTE YOUR NEW KEY HERE>"
```

Then reopen your terminal.

