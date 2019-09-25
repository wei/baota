import fetch  from 'isomorphic-unfetch'
import config from 'utils/../config.json'
import {loadCache} from 'utils/cache'

const GITHUB_TOKEN = process.env.GITHUB_TOKEN || null;

export default async (req, res) => {
    const {projects} = config
    const {owner, repo, platform, keyword, version} = req.query

    const projectData = config.projects.find(project => project.alias == `${owner}/${repo}`)

    if (!projectData) {
        return res.status(404).end()
    }

    const data = await Promise.all(projects.map(async project => {
        return {
            name: project.alias,
            releases: await loadCache(project.owner, project.repository, project.alias)
        }
    }))

    const project = data.find(project => project.name == `${owner}/${repo}`)

    if (!project) {
        res.status(404)
        res.end()
        return
    }

    const release = version === 'latest' ? project.releases[0] : project.releases.find(release => {
        return release.version.indexOf(version) !== -1
    })

    const file = release.files.find(file => {
        return (file.type || file.name).indexOf(platform) !== -1 && file.name.indexOf(keyword) != -1;
    })

    const result = await fetch(
        `https://${GITHUB_TOKEN}@api.github.com/repos/${projectData.owner}/${projectData.repository}/releases/assets/${file.id}`,
        { headers: { Accept: 'application/octet-stream' }, redirect: 'manual' }
    )

    if (result.status !== 302) {
        res.status(404)
        res.end()
        return
    }

    res.setHeader('Location', result.headers.get('Location'))
    res.status(302)
    res.end()
}
