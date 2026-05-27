const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'login', component: () => import('pages/LoginPage.vue') },
      { path: 'register', component: () => import('pages/RegisterPage.vue') },
      { path: 'forgot-password', component: () => import('pages/ForgotPasswordPage.vue') },
      { path: 'account/security', component: () => import('pages/AccountSecurityPage.vue') },
      { path: 'tools', component: () => import('pages/ToolsPage.vue') },
      { path: 'tools/mermaid', component: () => import('pages/tools/MermaidPage.vue') },
      { path: 'tools/csv', component: () => import('pages/tools/CsvPage.vue') },
      { path: 'tools/lol', component: () => import('pages/tools/LolPage.vue') },
      { path: 'tools/drawio', redirect: { path: '/tools/drawio/editor', query: { mode: 'diagram' } } },
      { path: 'admin', component: () => import('pages/AdminPage.vue') },
      { path: 'ui-preview', component: () => import('pages/UiPreviewPage.vue') },
      { path: 'auth/callback', component: () => import('pages/AuthCallbackPage.vue') }
    ]
  },
  {
    path: '/tools/drawio/editor',
    component: () => import('pages/tools/DrawioEditorPage.vue')
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
