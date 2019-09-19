import fetch  from 'isomorphic-unfetch'
import config from 'utils/../config.json'

const GITHUB_TOKEN = process.env.GITHUB_TOKEN || null;

export default async (req, res) => {
    const {owner, repo, version, id} = req.query
    const project = config.projects.find(project => project.alias == `${owner}/${repo}`)

    if (!project || !id || id == 'null') {
        return res.status(404).end()
    }

    const result = await fetch(
        `https://${GITHUB_TOKEN}@api.github.com/repos/${project.owner}/${project.repository}/releases/assets/${id}`,
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
