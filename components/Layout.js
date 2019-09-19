import Head from 'next/head'
import config from 'utils/../config.json'

export default ({title, children}) => (
    <main>
        <Head>
            <title>{config.title} - {title || 'Loading ...'}</title>
        </Head>

        <h1>{title}</h1>

        <section>
            {children}
        </section>

        <style jsx>{`
            :global(body) {
                box-sizing: border-box;
                padding: 20px;
                margin: 0;

                font-family: -apple-system, BlinkMacSystemFont,
                    "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell,
                    "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;

                background: black;
                color: white;

                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                text-rendering: optimizeLegibility;

                height: 100vh;
            }

            :global(body > div) {
                display: flex;
                align-items: center;
                height: 100%;
            }

            main {
                width: 550px;
                margin: 0 auto;
            }

            section {
                padding-right: 10px;
                max-height: calc(100vh - 300px);
                overflow-y: scroll;
            }

            h1 {
                margin-top: 0;
                margin-bottom: 50px;
            }

            /* Force Simple Scrollbars */
            :global(::-webkit-scrollbar) {
                -webkit-appearance: none;
                width: 10px;
            }
            :global(::-webkit-scrollbar-track) {
                background: rgba(0,0,0,0);
                border-radius: 0px;
            }
            :global(::-webkit-scrollbar-thumb) {
                cursor: pointer;
                border-radius: 5px;
                background: rgba(100, 100, 100, 0.25);
                transition: color 0.2s ease;
            }
            :global(::-webkit-scrollbar-thumb:window-inactive) {
                background: rgba(0, 0, 0, 0.15);
            }
            :global(::-webkit-scrollbar-thumb:hover) {
                background: rgba(128, 135, 139, 0.8);
            }
        `}</style>
    </main>
)
