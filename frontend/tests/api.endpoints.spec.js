import { describe, it, expect } from 'vitest'
import api, { authAPI, attractionsAPI, itineraryAPI } from '../src/services/api'

const spyAdapter = () => {
    const original = api.defaults.adapter
    const calls = []
    api.defaults.adapter = async (config) => {
        calls.push(config)
        return { status: 200, data: {}, statusText: 'OK', headers: {}, config }
    }
    return { calls, restore: () => (api.defaults.adapter = original) }
}

describe('api endpoints', () => {
    it('authAPI.login posts to /api/auth/login with body', async () => {
        const { calls, restore } = spyAdapter()
        try {
            const body = { email: 'a@b.c', password: 'p' }
            await authAPI.login(body)
            expect(calls).toHaveLength(1)
            expect(calls[0].method).toBe('post')
            expect(calls[0].url).toBe('/api/auth/login')
            const sent = typeof calls[0].data === 'string' ? JSON.parse(calls[0].data) : calls[0].data
            expect(sent).toEqual(body)
        } finally { restore() }
    })

    it('attractionsAPI.getAll GETs /api/attractions with params', async () => {
        const { calls, restore } = spyAdapter()
        try {
            const params = { city: 'Queenstown' }
            await attractionsAPI.getAll(params)
            expect(calls).toHaveLength(1)
            expect(calls[0].method).toBe('get')
            expect(calls[0].url).toBe('/api/attractions')
            expect(calls[0].params).toEqual(params)
        } finally { restore() }
    })

    it('itineraryAPI.plan posts to /api/itineraries/plan with payload', async () => {
        const { calls, restore } = spyAdapter()
        try {
            const payload = { user_id: 'u1', preferences: { duration: 2 } }
            await itineraryAPI.plan(payload)
            expect(calls).toHaveLength(1)
            expect(calls[0].method).toBe('post')
            expect(calls[0].url).toBe('/api/itineraries/plan')
            const sent = typeof calls[0].data === 'string' ? JSON.parse(calls[0].data) : calls[0].data
            expect(sent).toEqual(payload)
        } finally { restore() }
    })
})
