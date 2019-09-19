const config = require('../../config.json')
import {loadCache, bustCache} from 'utils/cache'

export default async (req, res) => {
    const {projects} = config

    if (req.query.cache == 'bust') {
        return bustCache(req, res)
    }

    const data = await Promise.all(projects.map(async project => {
        return {
            name: project.alias,
            releases: await loadCache(project.owner, project.repository, project.alias)
        }
    }))

    res.json(data)
}
