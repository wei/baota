import Error from 'next/error'
import MarkdownIt from 'markdown-it'
import Item from 'components/Item'
import Layout from 'components/Layout'
import Loader from 'components/Loader'

import {useRouter} from 'next/router'
import {useApi} from 'utils/api'

const markdownIt = MarkdownIt({
    html: true,
    linkify: true,
})

const Page = () => {
    const {query} = useRouter()
    const {owner, repo, version} = query
    const [projects, isLoading] = useApi('GET', '/api', [])

    const project = !isLoading && projects.find(project => project.name == `${owner}/${repo}`)
    const release = !isLoading && project && project.releases.find(release => release.version == version)

    if (!isLoading && (!project || !release)) {
        return <Error statusCode={404} />
    }

    return (
        <Layout title={!isLoading ? "版本详情" : ''}>
            {isLoading
                ? <Loader />
                : <>
                    <Item hasAll noNotes value={release} />

                    <section>
                        <h2>更新日志</h2>

                        <div dangerouslySetInnerHTML={{__html: markdownIt.render(release.notes.join('\n\n'))}}></div>

                        <style jsx>{`
                            h2 { margin-top: 50px; }
                        `}</style>
                    </section>
                </>
            }
        </Layout>
    )
}

export default Page
