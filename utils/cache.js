import fetch from 'isomorphic-unfetch'

const GITHUB_TOKEN = process.env.GITHUB_TOKEN || null;
const CACHE_DELAY = process.env.CACHE_DELAY || 1000 * 60 * 15; // minutes
const MAXIMUM_RELEASES = process.env.MAXIMUM_RELEASES || 25;
const PRE_RELEASES = process.env.PRE_RELEASES == "true";

let cachedData = {};

const isOutdated = key => {
    if (typeof cachedData[key] == "undefined") {
        return true;
    }

    return Date.now() > cachedData[key].expiresAt;
}

const refreshCache = async (owner, repo, alias) => {
    if (!GITHUB_TOKEN) {
        throw new Error('Token is not configured')
    }

    const url = `https://api.github.com/repos/${owner}/${repo}/releases?per_page=${MAXIMUM_RELEASES}`
    const headers = {
        Accept: 'application/vnd.github.preview',
        Authorization: `token ${GITHUB_TOKEN}`,
    }

    const response = await fetch(url, { headers })

    if (response.status !== 200) {
        throw new Error(`GitHub API responded with ${response.status} for url ${url}`)
    }

    const data = await response.json()

    if (!Array.isArray(data) || data.length === 0) {
        return
    }

    const releases = data
        .filter(item => item)
        .filter(item => !item.draft)
        .filter(item => PRE_RELEASES ? item.prerelease : !item.prerelease)
        .filter(item => item.assets && Array.isArray(item.assets) && item.assets.length > 0)

    const [aOwner, aRepo] = alias.split('/')

    cachedData[alias] = releases.map(release => {
        const newEntry = {
            owner: aOwner,
            repo: aRepo,
            name: release.name,
            date: release.published_at,
            version: release.tag_name,
            expiresAt: Date.now() + CACHE_DELAY,
            notes: (release.body || '')
                .split('*')
                .map(a => a.trim())
                .filter(a => a),
        }

        newEntry.notes.sort()

        newEntry.files = release.assets.map(asset => ({
            id: asset.id,
            name: asset.name,
            size: asset.size,
            type: asset.name.indexOf('win') === -1
                ? asset.name.indexOf('lin') === -1
                ? 'macos' : 'linux' : 'windows'
        }))

        return newEntry
    })

    return cachedData[alias]
}

const loadCache = async (owner, repo, alias) => {
    const key = `${owner}/${repo}`

    if (isOutdated(alias)) {
        await refreshCache(owner, repo, alias)
    }

    return cachedData[alias]
}

const bustCache = async (req, res) => {
    cachedData = [];
    res.end('')
}

module.exports = { loadCache, bustCache }
