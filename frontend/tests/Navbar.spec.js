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

describe('Navbar', () => {
    beforeEach(async () => {
        await router.replace('/')
        await router.isReady()
        localStorage.removeItem('token')
        localStorage.removeItem('userName')
    })

    it('renders brand title', async () => {
        const wrapper = mount(Navbar, { global: { plugins: [router] } })
        expect(wrapper.text()).toContain('Travel Planner')
    })

    it('shows Login/Register when logged out', async () => {
        const wrapper = mount(Navbar, { global: { plugins: [router] } })
        const text = wrapper.text()
        expect(text).toContain('Login')
        expect(text).toContain('Register')
    })

    it('shows user menu when logged in', async () => {
        localStorage.setItem('token', 'fake-token')
        localStorage.setItem('userName', 'Alice')
        const wrapper = mount(Navbar, { global: { plugins: [router] } })
        const text = wrapper.text()
        expect(text).toContain('My Page')
        expect(text).toContain('Alice')
        expect(text).not.toContain('Login')
        expect(text).not.toContain('Register')
    })
})
