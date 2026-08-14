# Publish this project on GitHub

This folder is prepared to be the **root of a GitHub repository**.

## Web-browser method

1. Create a new repository on GitHub.
2. For a broadly shared upstream project, choose **Public**. For your own personalized search, a **Private** fork/repository is recommended.
3. If you are uploading these prepared files, do not initialize the new repository with a different README/license/gitignore.
4. Upload the **contents of this folder**, including the hidden `.github` directory.
5. Commit the files.
6. Open the Actions tab and confirm you see:
   - `Tests`
   - `Daily biotech job search`
7. The daily-search workflow is manual-only in the public template. Personal users enable the schedule only after profile setup and a successful baseline run.

## Git command-line method

From inside this folder:

```bash
git init
git add .
git commit -m "Initial public release"
git branch -M main
git remote add origin YOUR_REPOSITORY_GIT_URL
git push -u origin main
```

## After publishing

Follow `docs/PUBLISHING_CHECKLIST.md`. GitHub recommends a clear README and, for open projects, supporting community files such as a license, contribution guidance, and security practices. This package includes those foundations.

For personal deployment, follow `docs/GITHUB_SETUP.md`.
