import { mount } from '@vue/test-utils'
import Navbar from '../src/components/Navbar.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { describe, it, expect, beforeEach } from 'vitest'

const router = createRouter({
    history: createWebHistory(),
    routes: [
    { path: '/', component: { template: '<div>home</div>' } },
    { path: '/login', component: { template: '<div>login</div>' } },
    { path: '/register', component: { template: '<div>register</div>' } },
    { path: '/user', component: { template: '<div>user</div>' } },
     ]
})

describe('Navbar links', () => {
    beforeEach(async () => {
        await router.replace('/')
        await router.isReady()
        localStorage.removeItem('token')
        localStorage.removeItem('userName')
    })

    it('brand link points to "/"', async () => {
        const wrapper = mount(Navbar, { global: { plugins: [router] } })
        const brand = wrapper.get('a.navbar-brand')
        expect(brand.text()).toContain('Travel Planner')
        expect(brand.attributes('href')).toBe('/')
    })
})
