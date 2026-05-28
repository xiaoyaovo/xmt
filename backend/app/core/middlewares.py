from fastapi.middleware.cors import CORSMiddleware


def apply_middlewares(app):
    return CORSMiddleware(
        app,
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
