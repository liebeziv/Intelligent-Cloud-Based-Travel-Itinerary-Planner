import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import api from '../src/services/api'

describe('api service', () => {
    let originalLocation

    beforeEach(() => {
        localStorage.removeItem('token')
        originalLocation = window.location
    })

    afterEach(() => {
        // restore the real location
        Object.defineProperty(window, 'location', {
            value: originalLocation,
            configurable: true,
            writable: false
        })
    })

    it('has a baseURL', () => {
        expect(api.defaults.baseURL).toBeTruthy()
    })

    it('clears token and redirects on 401', async () => {
        localStorage.setItem('token', 'to-be-cleared')

        const setHref = vi.fn()
        // redefine location with a configurable href accessor
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
        expect(setHref).toHaveBeenCalledWith('/login')
    })
})
