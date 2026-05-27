import os, httpx

r = httpx.post("https://api.resend.com/emails",
headers={"Authorization": f"Bearer re_ef4UXo4s_P9EfJWqCNddoHUMZj6ekBpAX"},
json={"from": "Xinming Tools <noreply@081189.xyz>",
"to": ["1430866820@qq.com"],
"subject": "Resend Test",
"html": "<h2>If you see this, Resend works</h2>",},)