# releases

A simple web-page/api resource that allows you to display the latest releases to your users and allow them to download them.
It is riented to work with and support private github repositories.

## Instructions

### Local development

1. `git clone`
2. `npm install`
3. Create a local config file based off of the `config.dest.json` via `cp config.dest.json config.json`
4. Edit it to reflect your needs
5. Run in develop mode to test it out locally `GITHUB_TOKEN=... npm run dev`

### Deployment (using now)

1. `now --prod -e GITHUB_TOKEN=...`

### Additional options

#### ENV
* `CACHE_DELAY=900000` - cache time for the specific release
* `MAXIMUM_RELEASES=25` - how many releases should be pulled from gihtub and displayed on `All releases` page

#### Config
* `config.prereleases=true/false` - do you want to display only pre-releases or stable releases

## Information

Ability to fetch a release directly by matched keywords:

```GET /api/fetch/[owner]/[repo]/[platform]/[keyword]/[version]```

Examples:

* `/api/fetch/inlife/releases/win/serv/latest`
* `/api/fetch/inlife/nexrender/lin/worker/1.23.2`


By default all releases are cached for 15 minutes. To bust cache (for example right after the release) you can call `GET /api?cache=bust`

The overall idea and design elements are based off the [ZEIT's Hazel](https://github.com/zeit/hazel/), props to them for making such a cool tool.
