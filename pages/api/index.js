const config = require('../../config.json')
import {loadCache} from 'utils/cache'

export default async (req, res) => {
    const {projects} = config

    const data = await Promise.all(projects.map(async project => {
        return {
            name: project.alias,
            releases: await loadCache(project.owner, project.repository, project.alias)
        }
    }))

    res.json(data)
}
