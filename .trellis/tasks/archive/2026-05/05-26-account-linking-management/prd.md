# 多账户绑定管理

## Goal

实现同一用户绑定多种登录方式，支持当前账号查看密码/GitHub/LinuxDo 绑定状态，并能在已登录状态下追加绑定或解绑第三方登录方式。后续新增微信、钉钉、OIDC 时复用同一数据模型和交互。

## What I Already Know

- 现有后端是 FastAPI + Tortoise ORM + Aerich，认证集中在 `backend/app/api/v1/auth.py`、`backend/app/services/auth_service.py`、`backend/app/models/user.py`。
- 现有前端是 Quasar + Vue 3 + Pinia，统一登录页已存在于 `frontend/src/pages/LoginPage.vue`，认证状态在 `frontend/src/stores/auth.js`。
- 当前 OAuth 登录已经有 GitHub 和 LinuxDo，但登录方式直接写在 `users` 表字段上，不适合一个用户多登录方式。
- 当前需求参考截图，需要一个“登录方式绑定”页面，显示邮箱/账号密码、GitHub、LinuxDo 等状态和操作。

## Requirements

- 新增 `user_auth_accounts` 表保存登录方式：`user_id`、`provider`、`provider_user_id`、展示名、邮箱、头像、密码 hash、绑定时间、最后使用时间。
- 登录时通过 `user_auth_accounts(provider, provider_user_id)` 找到主用户；找不到时创建新用户和首个登录方式。
- 密码登录通过 `user_auth_accounts` 校验，同时兼容迁移前 `users.password_hash` 数据。
- 已登录用户可查看绑定状态：password/github/linuxdo。
- 已登录用户可发起 GitHub/LinuxDo 绑定。OAuth state 必须签名，并区分 `login` 与 `link`。
- 已登录用户可解绑 GitHub/LinuxDo，但不能解绑最后一种登录方式。
- 不做自动合并：如果某个第三方账号已绑定到其他用户，返回冲突错误。
- 前端新增账号安全/绑定页面，入口放在用户菜单里。

## Acceptance Criteria

- [ ] `GET /api/v1/auth/accounts` 返回当前用户的绑定方式列表。
- [ ] `GET /api/v1/auth/github/link` 和 `GET /api/v1/auth/linuxdo/link` 返回可跳转 OAuth URL，且需要登录。
- [ ] OAuth 回调可处理登录和绑定两种目的。
- [ ] `DELETE /api/v1/auth/accounts/{provider}` 可解绑非最后一种非 password provider。
- [ ] 前端 `/account/security` 可展示绑定状态，点击绑定跳转 OAuth，解绑后刷新状态。
- [ ] 后端编译、Aerich heads、前端 lint/build 通过。

## Out Of Scope

- 自动合并两个已有账号的数据。
- 存储第三方 access token 并调用 provider 后续 API。
- 本任务不实现微信/钉钉/OIDC，只预留模型和前端样式。
