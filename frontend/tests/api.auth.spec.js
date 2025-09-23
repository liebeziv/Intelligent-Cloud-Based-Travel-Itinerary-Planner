import { describe, it, expect, beforeEach } from 'vitest'
import api from '../src/services/api'

const withAdapterSpy = (fn) => {
    const original = api.defaults.adapter
    const calls = []
    api.defaults.adapter = async (config) => {
        calls.push(config)
        return { status: 200, data: {}, statusText: 'OK', headers: {}, config }
    }
    return async () => {
        try { await fn(calls) } finally { api.defaults.adapter = original }
    }
}

describe('api auth header', () => {
    beforeEach(() => {
        localStorage.removeItem('token')
    })

    it('attaches Authorization when token exists', async () => {
        localStorage.setItem('token', 'abc123')
        await withAdapterSpy(async (calls) => {
            await api.get('/ping')
            expect(calls).toHaveLength(1)
            const auth = calls[0].headers?.Authorization
            expect(auth).toBe('Bearer abc123')
        })()
    })

    it('does not attach Authorization when token missing', async () => {
        await withAdapterSpy(async (calls) => {
            await api.get('/ping')
            expect(calls).toHaveLength(1)
            const auth = calls[0].headers?.Authorization
            expect(auth).toBeFalsy()
        })()
    })
})
