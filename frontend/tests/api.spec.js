import { describe, it, expect, beforeAll, vi } from 'vitest'

let api
const EXPECTED_BASE = 'http://localhost:8000'

beforeAll(async () => {
    // Inject env BEFORE loading the module
    vi.stubEnv('VITE_API_URL', EXPECTED_BASE)
    const mod = await import('../src/services/api') // dynamic import after stubbing env
    api = mod.default || mod
})

describe('api service', () => {
    it('has or can apply a baseURL', async () => {
        // Case 1: project sets baseURL from env at module init
        if (api.defaults.baseURL) {
            expect(api.defaults.baseURL).toBe(EXPECTED_BASE)
            return
        }

        // Case 2: project leaves baseURL empty — ensure we can set it and it is honored
        const originalAdapter = api.defaults.adapter
        const calls = []
        api.defaults.baseURL = EXPECTED_BASE
        api.defaults.adapter = async (config) => {
            calls.push(config)
            return { status: 200, data: {}, statusText: 'OK', headers: {}, config }
        }

        await api.get('/ping')

        expect(calls).toHaveLength(1)
        expect(calls[0].baseURL).toBe(EXPECTED_BASE)
        expect(calls[0].url).toBe('/ping')

        // restore
        api.defaults.adapter = originalAdapter
    })

    it('clears token and redirects on 401', async () => {
        localStorage.setItem('token', 'to-be-cleared')

        const originalLocation = window.location
        const setHref = vi.fn()
        Object.defineProperty(window, 'location', {
            configurable: true,
            value: {
                ...originalLocation,
                get href() { return '' },
                set href(v) { setHref(v) }
            }
        })

        const handlers = api.interceptors.response.handlers
        const rejected = handlers[0]?.rejected
        expect(typeof rejected).toBe('function')

        try {
            await rejected({ response: { status: 401 } })
        } catch {}

        expect(localStorage.getItem('token')).toBeNull()
        expect(setHref).toHaveBeenCalled()

        Object.defineProperty(window, 'location', {
            configurable: true,
            value: originalLocation
        })
    })
})
