# 新增登录页面

## Goal

新增统一登录页，支持账号密码、GitHub 和 LinuxDo 登录，让所有站内登录入口先进入同一个页面，再按用户选择进入对应认证流程。

## What I Already Know

- 前端是 Quasar + Vue 3，路由在 `frontend/src/router/routes.js`。
- 当前登录入口散落在布局、移动菜单、工具同步提示里，并且直接跳 GitHub OAuth。
- 后端当前只有 GitHub OAuth，用户表以 `github_id` 作为唯一身份字段。
- LinuxDo Connect 使用 OAuth2 授权码流程，公开端点为 authorize、token、user info。
- 当前 `backend/.env.example`、`backend/app/api/v1/auth.py`、`backend/app/settings/config.py` 已有未提交改动，实施时必须保留并顺着现状修改。

## Assumptions

- 账号密码登录先做“本地账号登录”，不开放公开注册。
- 本地账号可以通过配置的种子账号或数据库维护创建。
- OAuth 登录成功后继续使用现有 `/#/auth/callback` 统一接收 access token。

## Requirements

- 新增 `/login` 页面。
- 登录页支持账号密码表单，并展示 GitHub、LinuxDo 两个第三方登录按钮。
- 后端支持账号密码换取 JWT。
- 后端支持 LinuxDo OAuth 登录。
- GitHub、LinuxDo、本地账号统一序列化为当前用户信息。
- 现有“GitHub 登录”入口改成跳统一登录页。
- 保持工具页未登录时仍可本地使用，只有云同步/账号能力需要登录。

## Acceptance Criteria

- [ ] 访问 `/login` 可看到三种登录方式。
- [ ] 账号密码为空或错误时有明确错误提示。
- [ ] 账号密码登录成功后写入 token 并跳回目标页面。
- [ ] GitHub 按钮走现有 GitHub OAuth。
- [ ] LinuxDo 按钮跳转 LinuxDo Connect 授权端点。
- [ ] `/auth/me` 能返回不同 provider 的用户。
- [ ] `pnpm lint`、`pnpm build`、后端 `compileall` 通过。

## Definition of Done

- 后端模型、schema、迁移、配置与 API 更新完整。
- 前端路由、页面、store/lib 入口更新完整。
- 质量检查通过。
- 行为变化记录在 Trellis 任务文档中。

## Out of Scope

- 公开注册页面。
- 找回密码、修改密码、绑定/解绑多个 OAuth 账号。
- 完整账号设置页。

## Technical Notes

- LinuxDo Connect docs: authorize `https://connect.linux.do/oauth2/authorize`，token `https://connect.linux.do/oauth2/token`，user info `https://connect.linux.do/api/user`。
- 本地密码哈希使用标准库 PBKDF2-HMAC-SHA256，避免为一个小入口新增依赖。
