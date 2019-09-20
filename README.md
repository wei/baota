# releases

A simple web-page/api resource that allows you to display latest releases to your users and allow them to download those releases. Oriented to work and support private github repositories.

## Instructions

### Local development

1. `git clone`
2. `npm install`
3. `GITHUB_TOKEN=... npm run dev`

### Deployment (using now)

1. `now --prod -e GITHUB_TOKEN=...`

## Information

By default all releases are cached for 15 minutes. To bust cache (for example right after release) you can call `GET /api?cache=bust`
