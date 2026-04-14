# Vercel Deployment Guide

## Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=YOUR_REPO_URL)

## Prerequisites

- Vercel account (free tier works)
- GitHub/GitLab/Bitbucket repository with your code
- Environment variables configured (see below)

## Environment Variables

Set these in Vercel dashboard under **Settings > Environment Variables**:

| Variable | Description | Required |
|----------|-------------|----------|
| `API_KEY` | Your Deepseek/OpenAI API key | Yes |
| `API_BASE` | API base URL (e.g., `https://api.deepseek.com/v1`) | Yes |
| `MODEL_NAME` | Model name (e.g., `deepseek-chat`) | Yes |
| `MONGODB_URI` | MongoDB connection string | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon key | Yes |

## Deployment Steps

1. **Push your code to Git repository**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your Git repository

3. **Configure Build Settings**
   - Framework Preset: `Other`
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: (leave blank)
   - Install Command: `pip install -r requirements.txt`

4. **Add Environment Variables** (see table above)

5. **Deploy**
   - Click "Deploy"
   - Vercel will automatically deploy on every push

## Local Testing

Test Vercel deployment locally:

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Test deployment
vercel dev
```

## Troubleshooting

### Import Errors
- Ensure all dependencies are in `requirements.txt`
- Check that `api.py` exists at root level

### Runtime Errors
- Verify environment variables are set correctly
- Check database connections (MongoDB/Supabase)

### Static Files Not Loading
- Ensure `app/static` and `app/templates` directories exist
- Check file paths in the code

## Automatic Deployments

- **Push to main**: Production deployment
- **Push to branch**: Preview deployment
- **Pull Request**: Preview deployment for review

## Custom Domain

1. Go to Vercel dashboard
2. Navigate to your project settings
3. Click "Domains"
4. Add your custom domain
5. Update DNS records as instructed

## Support

For issues, check:
- Vercel function logs in dashboard
- Environment variables are properly configured
- All required files are committed to Git
