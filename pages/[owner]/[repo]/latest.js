import Head from 'next/head'
import Error from 'next/error'
import Item from 'components/Item'
import Layout from 'components/Layout'
import Loader from 'components/Loader'

import {useRouter} from 'next/router'
import {useApi} from 'utils/api'

import {redirectTo} from 'utils/redirect'

const Page = () => {
    const {query} = useRouter()
    const {owner, repo} = query
    const [projects, isLoading] = useApi('GET', '/api', [])
    const project = projects.find((project) => project.name == `${owner}/${repo}`)

    if (!isLoading && !project) {
        return <Error statusCode={404} />
    }

    /* show loader while waiting */
    if (isLoading) {
        return <Layout><Loader /></Layout>
    }


    let release = project.releases[0]

    if (!release || !release.version) {
        return <Error statusCode={404} />
    }

    redirectTo('/[owner]/[repo]/[version]', { as: `/${owner}/${repo}/${release.version}` });
    return <Layout></Layout>
}

export default Page
