import reflex as rx

config = rx.Config(
    app_name="code_server_panel",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)