# AMS FF Like — Full Stack

একটাই GitHub repo → একটাই Vercel URL → সব কিছু!

## URL গুলো

| URL | কাজ |
|-----|-----|
| `https://yourapp.vercel.app/` | User Panel |
| `https://yourapp.vercel.app/admin` | Admin Panel |
| `https://yourapp.vercel.app/like100` | Like 100 API |
| `https://yourapp.vercel.app/like200` | Like 200 API |

## GitHub → Vercel Deploy

### Step 1: GitHub এ upload করো
```
সব files GitHub repo তে push করো
```

### Step 2: Vercel এ connect করো
```
vercel.com → New Project → GitHub repo select করো
```

### Step 3: Environment Variables দাও
Vercel Dashboard → Settings → Environment Variables:
```
LIKE_API_100        = তোমার like 100 API URL
LIKE_API_200        = তোমার like 200 API URL  
LIKE_API_SECRET     = তোমার secret key
ADMIN_TOKEN         = ams_admin_2024_secret
APP_ENV             = production
```

### Step 4: Deploy!
Vercel automatically deploy করবে।

## Local এ চালাতে
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

## Admin Token
`ams_admin_2024_secret`
