import Error from 'next/error'
import Item from 'components/Item'
import Layout from 'components/Layout'
import Loader from 'components/Loader'

import {useRouter} from 'next/router'
import {useApi} from 'utils/api'

const Page = () => {
    const {query} = useRouter()
    const {owner, repo} = query
    const [projects, isLoading] = useApi('GET', '/api', [])
    const project = projects.find((project) => project.name == `${owner}/${repo}`)

    if (!isLoading && !project) {
        return <Error statusCode={404} />
    }

    return (
        <Layout title={!isLoading ? "宝塔版本" : ''}>
            {isLoading && projects.length < 1 &&  <Loader />}

            {project && project.releases.map((release, i) =>
                <Item key={i} value={release} />
            )}
        </Layout>
    )
}

export default Page
