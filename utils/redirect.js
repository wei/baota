// Packages
import React from 'react'
import Head from 'next/head'
import Router from 'next/router'

export function redirectTo(destination, { as, res, status } = {}) {
  if (res) {
    res.writeHead(status || 302, { Location: destination })
    res.end()
  } else {
    if (destination[0] === '/' && destination[1] !== '/') {
      Router.push(destination, as)
    } else {
      window.location = destination
    }
  }

  return null
}

const serialize = function(obj) {
  var str = [];
  for (var p in obj)
    if (obj[p]) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  return str.join("&");
}

export const redirect = (destination, keepQuery = false) =>
  class RedirectRoute extends React.Component {
    static getInitialProps({ res, query }) {
      if (typeof window === 'undefined' && !res.writeHead) {
        // This is the SSR mode
        return { metaRedirect: true }
      }

      if (keepQuery) {
        destination = `${destination}?${serialize(query)}`
      }

      redirectTo(destination, { res, status: 302 })
      return {}
    }

    render() {
      if (this.props.metaRedirect) {
        return (
          <Head>
            <meta httpEquiv="refresh" content={`0; url=${destination}`} />
          </Head>
        )
      }

      return null
    }
  }
