import {useState, useEffect} from 'react'
import fetch from 'isomorphic-unfetch'

let cacheBuster = 1;
let cache = {}

export const req = async (host, options) => {
    if (host[0] === '/') {
        host = location.origin + host
    }

    try {
        return await fetch(host, options)
    } catch (e) {
        return Promise.resolve({
            ok: false,
            error: e,
            json: async () => ({error: e})
        })
    }
}

export const useApi = (method, url, initialData, body = null) => {
    let didCancel = false;
    let didCache = false;

    if (cache.hasOwnProperty(url) && cache[url].method === method && cache[url].buster === cacheBuster) {
        const record = cache[url]

        didCache = true
        initialData = record.data;

        /* immidiately return cached version */
        if (record.timeout > Date.now()) {
            didCancel = true;
        }
    }

    const [state, setState] = useState({
        isLoading: true,
        isError: false,
        data: initialData,
    });

    useEffect(() => {
        const fetchData = async () => {
            if (didCache) setState({ isLoading: false, data: initialData, isError: false })
            if (didCancel) return

            try {
                const res = await req(url, { method })
                const result = await res.json()

                if (!res.ok) {
                    console.error(result)
                    throw new Error(result.error)
                }

                let record = {
                    timeout: Date.now() + 10000,
                    method: method,
                    data: result,
                    buster: cacheBuster,
                }

                cache[url] = record

                if (!didCancel) {
                    setState({ isLoading: false, isError: false, data: result });
                }
            } catch (error) {
                if (!didCancel) {
                    setState({ isLoading: false, isError: true, data: initialData });
                }
            }
        };

        fetchData();

        return () => { didCancel = true; };
      }, [cacheBuster, url, body]);

      return [state.data, state.isLoading];
}

export const bustCache = () => {
    cacheBuster++
}
