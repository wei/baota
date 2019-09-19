import Head from 'next/head'
import Item from 'components/Item'
import Layout from 'components/Layout'
import Loader from 'components/Loader'
import {useApi} from 'utils/api'

const Page = () => {
    const [projects, isLoading] = useApi('GET', '/api', [])

    return (
        <Layout title={!isLoading ? "Latest releases" : ''}>
            <Head>
                <title>{isLoading ? 'Loading ...' : 'Latest releases'}</title>
            </Head>

            {isLoading && projects.length < 1 &&  <Loader />}

            {projects.map((project, i) =>
                <Item key={i} hasAll value={project.releases[0]} />
            )}
        </Layout>
    )
}

export default Page
