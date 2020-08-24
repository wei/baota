import Link from 'next/link'
import {formatDistanceToNow} from 'date-fns'
import config from 'utils/../config.json'

const IS_PRERELEASE = config.prereleases;

const Item = ({ value, hasAll, noNotes }) => (
    <article>
        <header>
            <div className="release"><span className="repo">{value.repo}</span><small> @ </small><small className="version">{value.version}</small></div>
            <Link href='/[owner]/[repo]/[version]' as={`/${value.owner}/${value.repo}/${value.version}`}>
                <a className="date">{value.notes[0].match(/\d{4}-\d{2}-\d{2}/)}</a>
            </Link>
        </header>

        {value.files.map((file, i) =>
            <div key={i} className="item">
                <div className="fileType">
                    <span className="url">
                        <a href={`/api/download/${value.owner}/${value.repo}/${value.version}/${file.id}`}>{file.name}</a>
                    </span>
                </div>
                <div className="size">{(file.size/1000/1000).toFixed(2)} MB</div>
            </div>
        )}

        <footer>
            <div className="version">{value.version.indexOf('v')===0?'':'v'}{value.version}</div>

            {noNotes ? null :
                <Link href='/[owner]/[repo]/[version]' as={`/${value.owner}/${value.repo}/${value.version}`}>
                    <a className="release-notes">Release Notes</a>
                </Link>
            }

            {!hasAll ? null :
                <div className="all-releases">
                    <Link href='/[owner]/[repo]' as={`/${value.owner}/${value.repo}`}><a>查看历史版本</a></Link>
                </div>
            }
        </footer>

        <style jsx>{`
            article { margin: 75px 0; }
            :global(article:first-child) { margin-top: 0; }
            :global(article:last-of-type) { margin-bottom: 0; }

            header {
                display: flex;
                align-items: center;
                font-size: 24px;
                margin-bottom: 40px;
            }

            a.release:hover, a.date:hover {
                text-decoration: underline;
                cursor: pointer;
            }

            .release {
                flex-grow: 1;
                color: white;
                text-decoration: none;
            }

            .repo { font-weight: 800; }
            .url { font-weight: 400; }

            .date {
                text-decoration: none;
                color: gray;
                font-size: 18px;
            }

            .size {
                color: #404040;
                white-space: nowrap;
            }

            footer {
                display: flex;
                align-items: center;
                flex-wrap: wrap;
            }

            footer > * {
                margin-top: 40px;
            }

            footer a {
                color: gray;
                text-decoration: none;
            }

            footer a:hover {
                text-decoration: underline;
            }

            .version {
                margin-right: 8px;
                padding: 2px 6px;
                border-radius: 4px;
                background: ${IS_PRERELEASE
                    ? 'linear-gradient(#258c2b, #44f638);'
                    : 'linear-gradient(#ff00a5, #f65538);'
                }
            }

            .release-notes {
                font-weight: 600;
                color: white;
            }

            .all-releases {
                text-align: right;
                flex-grow: 1;
            }

            .item {
                display: flex;
                align-items: center;
            }

            .item:not(:last-of-type) {
                margin-bottom: 4px;
            }

            .item a {
                color: ${IS_PRERELEASE ? '#03ff8f;' : '#ff0387;' }
                text-decoration: none;
            }

            .item a:hover {
                text-decoration: underline;
            }

            .fileType {
                font-weight: 600;
                flex-grow: 1;
            }

            .url {
                font-weight: 400;
            }

            .size {
                color: #404040;
                white-space: nowrap;
            }
        `}</style>
    </article>
)

export default Item
