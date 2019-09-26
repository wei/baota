# releases


A simple web-page/api resource that allows you to display the latest releases to your users and allow them to download them.
It is riented to work with and support private github repositories.

![](https://user-images.githubusercontent.com/2182108/65677990-3ce81800-e05b-11e9-8750-4e116048d3e0.png)

> Example page: [nexrender.now.sh](https://nexrender.now.sh/)

It is based on the same idea, design, and principles established by [ZEIT's Hazel](https://github.com/zeit/hazel/) (which is an amazing tool on it's own).

However this is a more general version with intention to support:

* Support for any kind of applications/binary artifacts/etc
* Support of multiple repositories even from different owners (projects) at the same time
* Support private repositories by default
* Repository name and owner aliasing (to override the display names for your private repos)
* Leverages GitHub releases, as well as git tag versioning approach

## Instructions

### Local development

1. `git clone https://github.com/inlife/releases.git`
2. `cd releases`
2. `npm install`
3. `cp config.dest.json config.json`
4. Edit config to reflect your needs
5. `GITHUB_TOKEN=... npm run dev`

### Deployment (using now)

1. `now --prod -e GITHUB_TOKEN=...`

### Additional options

#### ENV
* `CACHE_DELAY=900000` - cache time for the specific release
* `MAXIMUM_RELEASES=25` - how many releases should be pulled from gihtub and displayed on `All releases` page

#### Config
* `config.prereleases=true/false` - do you want to display only pre-releases or stable releases

## Routes

### /

Displays information about latest releas for each one of the configured projects.

### /[owner]/[repo]/

Display a set of releases for a specific repository.

### /[owner]/[repo]/[version]

Display a detailed information about a specific release, including it's release notes.

> You can also provide `latest` as version name to auto-redirect to the latest available release.

### /api

Get infromation in the JSON format about all projects with a single call.

### /api/download/[owner]/[repo]/[version]/[assetId]

Get a direct proxied download link for the specific asset (can be retrieved from `/api` call).

### /api/fetch/[onwer]/[repo]/[platform]/[keyword]/[version]

Auto-guess and get a direct download link for an asset matching provided criteria.

Both `platform` and `keyword` are used to search for the match inside of the asset label string.

#### Examples:

Assuming your asset name would look like: `myasset-win-server-v12.3.exe`, or `myasset-linux-worker-1.23.2`, both cases below would return the appropriate asset respectively:

* `/api/fetch/inlife/releases/win/serv/latest`
* `/api/fetch/inlife/nexrender/lin/worker/1.23.2`

By default all releases are cached for 15 minutes. To bust cache (for example right after the release) you can call `GET /api?cache=bust`

## Credits

Huge thanks to Leo Lamprecht ([@leo](https://github.com/leo)) - [ZEIT](https://zeit.co) for creating [Hazel](https://github.com/zeit/hazel/)
