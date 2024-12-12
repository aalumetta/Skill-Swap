import flet as ft
from datetime import datetime


class Skill:
    def __init__(self, name, level, description):
        self.name = name
        self.level = level
        self.description = description
        self.date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"{self.name} (Level: {self.level})"


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.skills = []
        self.friends = []
        self.trade_requests = []
        self.messages = {}  # Store messages with friend usernames as keys

    def add_skill(self, skill):
        self.skills.append(skill)

    def add_friend(self, friend_username):
        self.friends.append(friend_username)
        self.messages[friend_username] = []  # Initialize a message list for the new friend

    def propose_trade(self, skill_name, friend_username):
        self.trade_requests.append((skill_name, friend_username))

    def accept_trade(self, skill_name):
        for request in self.trade_requests:
            if request[0] == skill_name:
                self.trade_requests.remove(request)
                return f"Trade accepted: {skill_name}"
        return "Trade not found."

    def decline_trade(self, skill_name):
        for request in self.trade_requests:
            if request[0] == skill_name:
                self.trade_requests.remove(request)
                return f"Trade declined: {skill_name}"
        return "Trade not found."


class UserDatabase:
    def __init__(self):
        self.users = {}

    def register_user(self, username, password):
        if username in self.users:
            raise Exception("User already exists!")
        self.users[username] = User(username, password)

    def login_user(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            return user
        raise Exception("Invalid username or password!")

    def get_user_by_username(self, username):
        return self.users.get(username)


def main(page: ft.Page):
    page.title = "SkillSwap App"
    page.bgcolor = "#E3F2FD"
    current_user = None
    user_db = UserDatabase()

    # Input fields
    username_input = ft.TextField(label="Username", width=250)
    password_input = ft.TextField(label="Password", password=True, width=250)
    skill_name_input = ft.TextField(label="Skill Name", width=250)
    skill_level_input = ft.Dropdown(label="Skill Level", options=[
        ft.dropdown.Option("Beginner"),
        ft.dropdown.Option("Intermediate"),
        ft.dropdown.Option("Expert"),
    ])
    friend_input = ft.TextField(label="Add Friend", width=250)
    trade_skill_input = ft.Dropdown(label="Select Skill to Trade", width=250)
    message_area = ft.Text(value="", color="#D32F2F")

    # Profile settings fields
    profile_username_input = ft.TextField(label="New Username", width=250)
    profile_password_input = ft.TextField(label="New Password", password=True, width=250)
    delete_account_input = ft.TextField(label="Confirm Username to Delete Account", width=250)

    # Messaging components
    message_input = ft.TextField(label="Message", width=250)
    send_message_button = ft.ElevatedButton("Send", bgcolor="#4CAF50", color="#FFFFFF")
    chat_area = ft.Column()

    def update_trade_skill_list():
        if current_user:
            trade_skill_input.options = [ft.dropdown.Option(skill.name) for skill in current_user.skills]
            trade_skill_input.update()

    def update_trade_requests():
        if current_user:
            trade_request_area.controls.clear()
            for skill_name, friend_username in current_user.trade_requests:
                trade_request_area.controls.append(
                    ft.Row(
                        [
                            ft.Text(f"Trade: {skill_name} from {friend_username}"),
                            ft.ElevatedButton("Accept", on_click=lambda e, sn=skill_name: handle_accept_trade(sn), bgcolor="#4CAF50", color="#FFFFFF"),
                            ft.ElevatedButton("Decline", on_click=lambda e, sn=skill_name: handle_decline_trade(sn), bgcolor="#D32F2F", color="#FFFFFF"),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                )
            trade_request_area.update()

    def update_chat_area(friend_username):
        chat_area.controls.clear()
        if current_user and friend_username in current_user.messages:
            for msg in current_user.messages[friend_username]:
                chat_area.controls.append(ft.Text(f"{friend_username}: {msg}"))
        chat_area.update()

    def handle_register(e):
        try:
            user_db.register_user(username_input.value, password_input.value)
            message_area.value = "Registration successful! Please log in."
            message_area.color = "#388E3C"
            message_area.update()
        except Exception as ex:
            message_area.value = f"Error: {str(ex)}"
            message_area.color = "#D32F2F"
            message_area.update()

    def handle_login(e):
        nonlocal current_user
        try:
            current_user = user_db.login_user(username_input.value, password_input.value)
            message_area.value = f"Welcome, {current_user.username}!"
            message_area.color = "#388E3C"
            message_area.update()
            update_trade_skill_list()
            update_trade_requests()
            # Show Manage Skills, Friends, and Profile Settings tabs
            manage_skills_tab.visible = True
            friends_tab.visible = True
            profile_settings_tab.visible = True
            messaging_tab.visible = True
            tabs.update()  # Refresh the tab view
        except Exception as ex:
            message_area.value = f"Login failed: {str(ex)}"
            message_area.color = "#D32F2F"
            message_area.update()

    def handle_add_skill(e):
        if current_user is None:
            message_area.value = "Please log in to add skills."
            message_area.color = "#D32F2F"
            message_area.update()
            return
        skill = Skill(skill_name_input.value, skill_level_input.value, "")
        current_user.add_skill(skill)
        message_area.value = f"Added skill: {skill.name}"
        message_area.color = "#388E3C"
        message_area.update()
        update_trade_skill_list()

    def handle_add_friend(e):
        if current_user is None:
            message_area.value = "Please log in to add friends."
            message_area.color = "#D32F2D"
            message_area.update()
            return
        current_user.add_friend(friend_input.value)
        message_area.value = f"Friend added: {friend_input.value}"
        message_area.color = "#388E3C"
        message_area.update()

    def handle_propose_trade(e):
        if current_user is None:
            message_area.value = "Please log in to propose trades."
            message_area.color = "#D32F2D"
            message_area.update()
            return
        friend_username = friend_input.value
        skill_name = trade_skill_input.value
        if friend_username and skill_name:
            user_to_trade = user_db.get_user_by_username(friend_username)
            if user_to_trade:
                user_to_trade.propose_trade(skill_name, current_user.username)
                message_area.value = f"Trade proposed: {skill_name} to {friend_username}"
                message_area.color = "#388E3C"
            else:
                message_area.value = "Friend not found."
                message_area.color = "#D32F2D"
        else:
            message_area.value = "Please select a skill and enter a friend's username."
            message_area.color = "#D32F2D"
        message_area.update()

    def handle_accept_trade(skill_name):
        result = current_user.accept_trade(skill_name)
        message_area.value = result
        message_area.color = "#388E3C" if "accepted" in result else "#D32F2D"
        message_area.update()
        update_trade_requests()

    def handle_decline_trade(skill_name):
        result = current_user.decline_trade(skill_name)
        message_area.value = result
        message_area.color = "#388E3C" if "declined" in result else "#D32F2D"
        message_area.update()
        update_trade_requests()

    def handle_update_profile(e):
        global current_user
        new_username = profile_username_input.value
        new_password = profile_password_input.value
        
        if new_username:
            if new_username in user_db.users:
                message_area.value = "Username already exists!"
                message_area.color = "#D32F2D"
                message_area.update()
                return
            user_db.users.pop(current_user.username)  # Remove old user entry
            current_user.username = new_username
            user_db.users[new_username] = current_user  # Add updated user
        if new_password:
            current_user.password = new_password

        message_area.value = "Profile updated successfully!"
        message_area.color = "#388E3C"
        message_area.update()

    def handle_delete_account(e):
        global current_user
        username_to_delete = delete_account_input.value
        
        if username_to_delete == current_user.username:
            del user_db.users[current_user.username]
            current_user = None  # Clear current user
            message_area.update()
        else:
            message_area.value = "Username does not match!"
            message_area.color = "#D32F2D"
            message_area.update()

    def handle_send_message(e):
        if current_user is None:
            message_area.value = "Please log in to send messages."
            message_area.color = "#D32F2D"
            message_area.update()
            return
        friend_username = friend_input.value
        message_text = message_input.value
        if friend_username and message_text:
            current_user.send_message(friend_username, message_text)
            message_area.value = f"Message sent to {friend_username}: {message_text}"
            message_area.color = "#388E3C"
            message_input.value = ""  # Clear the message input
            update_chat_area(friend_username)  # Update the chat area
        else:
            message_area.value = "Please enter a friend's username and a message."
            message_area.color = "#D32F2D"
        message_area.update()

    # UI components
    trade_request_area = ft.Column()

    manage_skills_tab = ft.Tab(
        text="Manage Skills",
        content=ft.Container(
            content=ft.Column(
                [
                    skill_name_input,
                    skill_level_input,
                    ft.ElevatedButton("Add Skill", on_click=handle_add_skill, bgcolor="#4CAF50", color="#FFFFFF"),
                ]
            ),
            padding=ft.padding.all(20)
        ),
    )
    manage_skills_tab.visible = False  # Initially hidden

    friends_tab = ft.Tab(
        text="Friends",
        content=ft.Container(
            content=ft.Column(
                [
                    friend_input,
                    ft.ElevatedButton("Add Friend", on_click=handle_add_friend, bgcolor="#4CAF50", color="#FFFFFF"),
                    trade_skill_input,
                    ft.ElevatedButton("Propose Trade", on_click=handle_propose_trade, bgcolor="#FF9800", color="#FFFFFF"),
                    ft.Text("Trade Requests:"),
                    trade_request_area
                ]
            ),
            padding=ft.padding.all(20)
        ),
    )
    friends_tab.visible = False  # Initially hidden

    profile_settings_tab = ft.Tab(
        text="Profile Settings",
        content=ft.Container(
            content=ft.Column(
                [
                    profile_username_input,
                    profile_password_input,
                    ft.ElevatedButton("Update Profile", on_click=handle_update_profile, bgcolor="#4CAF50", color="#FFFFFF"),
                    delete_account_input,
                    ft.ElevatedButton("Delete Account", on_click=handle_delete_account, bgcolor="#D32F2F", color="#FFFFFF"),
                ]
            ),
            padding=ft.padding.all(20)
        ),
    )
    profile_settings_tab.visible = False  # Initially hidden

    messaging_tab = ft.Tab(
        text="Messaging",
        content=ft.Container(
            content=ft.Column(
                [
                    friend_input,  # Reuse friend input for messaging
                    message_input,
                    send_message_button,
                    ft.Text("Chat:"),
                    chat_area,
                ]
            ),
            padding=ft.padding.all(20)
        ),
    )
    messaging_tab.visible = False  # Initially hidden

    send_message_button.on_click = handle_send_message  # Link the button to the send message function

    # Tabs
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="Login/Register",
                content=ft.Container(
                    content=ft.Column(
                        [
                            username_input,
                            password_input,
                            ft.Row(
                                [
                                    ft.ElevatedButton("Login", on_click=handle_login, bgcolor="#1565C0", color="#FFFFFF"),
                                    ft.ElevatedButton("Register", on_click=handle_register, bgcolor="#4CAF50", color="#FFFFFF"),
                                ]
                            ),
                            message_area,
                        ]
                    ),
                    padding=ft.padding.all(20)
                ),
            ),
            manage_skills_tab,
            friends_tab,
            profile_settings_tab,
            messaging_tab,
        ],
        expand=1,
    )

    page.add(tabs)


ft.app(target=main)