import reflex as rx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi_radar import Radar
from sqlalchemy import create_engine


class SidebarState(rx.State):
    sidebar_open: bool = True

    @rx.event
    def toggle_sidebar(self):
        self.sidebar_open = not self.sidebar_open


class RBACState(rx.State):
    roles: list[dict[str, str]] = [
        {"id": "1", "role": "Admin", "permissions": "Full Access", "users": "5"},
        {"id": "2", "role": "Editor", "permissions": "Read, Write", "users": "12"},
        {"id": "3", "role": "Viewer", "permissions": "Read Only", "users": "25"},
        {"id": "4", "role": "Manager",
            "permissions": "Read, Write, Approve", "users": "8"},
    ]

    # Form fields
    edit_id: str = ""
    role_name: str = ""
    permissions: str = ""
    users_count: str = ""
    is_editing: bool = False
    show_form: bool = False

    @rx.event
    def toggle_form(self):
        self.show_form = not self.show_form
        if not self.show_form:
            self.clear_form()

    @rx.event
    def clear_form(self):
        self.role_name = ""
        self.permissions = ""
        self.users_count = ""
        self.edit_id = ""
        self.is_editing = False
        self.show_form = False

    @rx.event
    def add_role(self):
        if self.role_name and self.permissions:
            new_id = str(len(self.roles) + 1)
            self.roles.append({
                "id": new_id,
                "role": self.role_name,
                "permissions": self.permissions,
                "users": self.users_count or "0",
            })
            self.clear_form()
            self.show_form = False

    @rx.event
    def edit_role(self, role_id: str):
        role = next((r for r in self.roles if r["id"] == role_id), None)
        if role:
            self.edit_id = role_id
            self.role_name = role["role"]
            self.permissions = role["permissions"]
            self.users_count = role["users"]
            self.is_editing = True
            self.show_form = True

    @rx.event
    def update_role(self):
        if self.edit_id and self.role_name and self.permissions:
            for role in self.roles:
                if role["id"] == self.edit_id:
                    role["role"] = self.role_name
                    role["permissions"] = self.permissions
                    role["users"] = self.users_count or "0"
                    break
            self.clear_form()
            self.show_form = False

    @rx.event
    def delete_role(self, role_id: str):
        self.roles = [r for r in self.roles if r["id"] != role_id]

    @rx.event
    def set_role_name(self, role_name: str):
        self.role_name = role_name

    @rx.event
    def set_permissions(self, permissions: str):
        self.permissions = permissions

    @rx.event
    def set_users_count(self, users_count: str):
        self.users_count = users_count


def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "border-radius": "0.5em",
            },
        ),
        href=href,
        underline="none",
        weight="medium",
        width="100%",
    )


def sidebar_items() -> rx.Component:
    return rx.vstack(
        sidebar_item("Dashboard", "layout-dashboard", "/"),
        sidebar_item("Projects", "square-library", "/#"),
        sidebar_item("Analytics", "bar-chart-4", "/#"),
        sidebar_item("Messages", "mail", "/#"),
        spacing="1",
        width="100%",
    )


def sidebar_top_profile() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.vstack(
                rx.hstack(
                    rx.cond(
                        SidebarState.sidebar_open,
                        rx.hstack(
                            rx.icon_button(rx.icon("user"),
                                           size="3", radius="full"),
                            rx.vstack(
                                rx.box(
                                    rx.text("My account", size="3",
                                            weight="bold"),
                                    rx.text("user@reflex.dev",
                                            size="2", weight="medium"),
                                    width="100%",
                                ),
                                spacing="0",
                                justify="start",
                                width="100%",
                            ),
                            rx.spacer(),
                            rx.icon_button(
                                rx.icon("settings"),
                                size="2",
                                variant="ghost",
                                color_scheme="gray",
                            ),
                            align="center",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.icon_button(rx.icon("user"),
                                           size="3", radius="full"),
                            align="center",
                            width="100%",
                            justify="center",
                        ),
                    ),
                    padding_x="0.5rem",
                    align="center",
                    width="100%",
                ),
                rx.cond(
                    SidebarState.sidebar_open,
                    sidebar_items(),
                    rx.vstack(
                        rx.icon_button(rx.icon("layout-dashboard"),
                                       variant="ghost", size="2"),
                        rx.icon_button(rx.icon("square-library"),
                                       variant="ghost", size="2"),
                        rx.icon_button(rx.icon("bar-chart-4"),
                                       variant="ghost", size="2"),
                        rx.icon_button(rx.icon("mail"),
                                       variant="ghost", size="2"),
                        spacing="2",
                        width="100%",
                        align="center",
                    ),
                ),
                rx.spacer(),
                rx.cond(
                    SidebarState.sidebar_open,
                    sidebar_item("Help & Support", "life-buoy", "/#"),
                    rx.icon_button(rx.icon("life-buoy"),
                                   variant="ghost", size="2"),
                ),
                rx.divider(margin="0.5em 0"),
                rx.hstack(
                    rx.icon_button(
                        rx.cond(
                            SidebarState.sidebar_open,
                            rx.icon("chevron-left"),
                            rx.icon("chevron-right"),
                        ),
                        on_click=SidebarState.toggle_sidebar,
                        size="2",
                        variant="ghost",
                        color_scheme="gray",
                    ),
                    width="100%",
                    justify="center",
                ),
                spacing="5",
                padding_x="1em",
                padding_y="1.5em",
                bg=rx.color("accent", 3),
                align="start",
                height="100vh",
                width=rx.cond(SidebarState.sidebar_open, "16em", "5em"),
                transition="width 0.3s ease",
            ),
        ),
        rx.mobile_and_tablet(
            rx.drawer.root(
                rx.drawer.trigger(rx.icon("align-justify", size=30)),
                rx.drawer.overlay(z_index="5"),
                rx.drawer.portal(
                    rx.drawer.content(
                        rx.vstack(
                            rx.box(
                                rx.drawer.close(rx.icon("x", size=30)),
                                width="100%",
                            ),
                            sidebar_items(),
                            rx.spacer(),
                            rx.vstack(
                                sidebar_item("Help & Support",
                                             "life-buoy", "/#"),
                                rx.divider(margin="0"),
                                rx.hstack(
                                    rx.icon_button(
                                        rx.icon("user"), size="3", radius="full"
                                    ),
                                    rx.vstack(
                                        rx.box(
                                            rx.text(
                                                "My account", size="3", weight="bold"
                                            ),
                                            rx.text(
                                                "user@reflex.dev",
                                                size="2",
                                                weight="medium",
                                            ),
                                            width="100%",
                                        ),
                                        spacing="0",
                                        justify="start",
                                        width="100%",
                                    ),
                                    padding_x="0.5rem",
                                    align="center",
                                    justify="start",
                                    width="100%",
                                ),
                                width="100%",
                                spacing="5",
                            ),
                            spacing="5",
                            width="100%",
                        ),
                        top="auto",
                        right="auto",
                        height="100%",
                        width="20em",
                        padding="1.5em",
                        bg=rx.color("accent", 2),
                    ),
                    width="100%",
                ),
                direction="left",
            ),
            padding="1em",
        ),
    )


def rbac_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(RBACState.is_editing, "Edit Role", "Add New Role"),
            ),
            rx.dialog.description(
                rx.cond(
                    RBACState.is_editing,
                    "Update the role information below.",
                    "Fill in the details to create a new role.",
                ),
            ),
            rx.vstack(
                rx.input(
                    placeholder="Role Name (e.g., Admin, Editor)",
                    value=RBACState.role_name,
                    on_change=RBACState.set_role_name,
                    width="100%",
                ),
                rx.input(
                    placeholder="Permissions (e.g., Read, Write, Delete)",
                    value=RBACState.permissions,
                    on_change=RBACState.set_permissions,
                    width="100%",
                ),
                rx.input(
                    placeholder="Number of Users",
                    value=RBACState.users_count,
                    on_change=RBACState.set_users_count,
                    width="100%",
                    type="number",
                ),
                spacing="4",
                width="100%",
                margin_top="1em",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=RBACState.clear_form,
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        rx.cond(RBACState.is_editing, "Update", "Add Role"),
                        on_click=rx.cond(
                            RBACState.is_editing,
                            RBACState.update_role,
                            RBACState.add_role,
                        ),
                        color_scheme="green",
                    ),
                ),
                spacing="3",
                width="100%",
                justify="end",
                margin_top="1.5em",
            ),
            max_width="500px",
        ),
        open=RBACState.show_form,
    )


def show_role(role: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(role["role"]),
        rx.table.cell(role["permissions"]),
        rx.table.cell(role["users"]),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil"),
                    size="2",
                    variant="soft",
                    color_scheme="blue",
                    on_click=lambda: RBACState.edit_role(role["id"]),
                ),
                rx.icon_button(
                    rx.icon("trash-2"),
                    size="2",
                    variant="soft",
                    color_scheme="red",
                    on_click=lambda: RBACState.delete_role(role["id"]),
                ),
                spacing="2",
            )
        ),
    )


def rbac_table() -> rx.Component:
    return rx.vstack(
        rbac_form(),
        rx.hstack(
            rx.heading("RBAC Management", size="7"),
            rx.spacer(),
            rx.button(
                rx.icon("plus"),
                "Add Role",
                on_click=RBACState.toggle_form,
                color_scheme="green",
            ),
            width="100%",
            align="center",
            margin_bottom="1em",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Role"),
                    rx.table.column_header_cell("Permissions"),
                    rx.table.column_header_cell("Users"),
                    rx.table.column_header_cell("Actions"),
                ),
            ),
            rx.table.body(
                rx.foreach(RBACState.roles, show_role),
            ),
            variant="surface",
            size="3",
            width="100%",
        ),
        width="100%",
        padding="2em",
        spacing="4",
    )


def dashboard() -> rx.Component:
    return rx.flex(
        rx.hstack(
            sidebar_top_profile(),
            rbac_table(),
            height="100vh",
            width="100%",
            align="start",
        ),
        height="100vh",
        width="100%",
    )


def index() -> rx.Component:
    return dashboard()


# Create FastAPI app
fastapi_app = FastAPI()
engine = create_engine("sqlite:///./app.db")

# Full monitoring with SQL query tracking
radar = Radar(fastapi_app, db_engine=engine)
radar.create_tables()


@fastapi_app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "service": "code-server-panel"})


@fastapi_app.get("/api/roles")
async def get_roles():
    """Get all RBAC roles"""
    # In a real app, this would fetch from a database
    return JSONResponse({
        "roles": [
            {"id": "1", "role": "Admin", "permissions": "Full Access", "users": "5"},
            {"id": "2", "role": "Editor", "permissions": "Read, Write", "users": "12"},
            {"id": "3", "role": "Viewer", "permissions": "Read Only", "users": "25"},
            {"id": "4", "role": "Manager",
                "permissions": "Read, Write, Approve", "users": "8"},
        ]
    })


@fastapi_app.post("/api/roles")
async def create_role(role: dict):
    """Create a new RBAC role"""
    return JSONResponse({"message": "Role created", "role": role})


# Mount the FastAPI router to Reflex's underlying FastAPI app
app = rx.App(api_transformer=fastapi_app)
app.add_page(index)
