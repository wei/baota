# releases

A simple web-page/api resource that allows you to display latest releases to your users and allow them to download those releases. Oriented to work and support private github repositories.

## Instructions

### Local development

1. `git clone`
2. `npm install`
3. Create a local config file based off the `config.dest.json` via `cp config.dest.json config.json`
4. Edit it to reflect your needs
5. Run in develop mode to test it out locally `GITHUB_TOKEN=... npm run dev`

### Deployment (using now)

1. `now --prod -e GITHUB_TOKEN=...`

## Information

By default all releases are cached for 15 minutes. To bust cache (for example right after release) you can call `GET /api?cache=bust`

The overall idea and design elements are based off the [ZEIT's Hazel](https://github.com/zeit/hazel/), props to them for making such a cool tool.
