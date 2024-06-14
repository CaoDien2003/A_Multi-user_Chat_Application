# Chat Application

## Overview

This is a multi-user chat application that allows users to create and join group chats. It features user authentication, private messaging, group chat rooms, and persistent user display on the dashboard.

## Features

- User authentication via tokens
- Private messaging between users
- Creation and joining of group chat rooms
- Persistent user display on the dashboard
- WebSocket communication for real-time chat

## Prerequisites

- Python 3.x
- MongoDB
- Virtual environment (recommended)

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/CaoDien2003/A_Multi-user_Chat_Application.git
    cd A_Multi-user_Chat_Application
    ```

2. **Set Up Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    .\venv\Scripts\activate  # On Windows
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up MongoDB:**

    Ensure MongoDB is installed and running on your machine. Update the MongoDB connection string in your code if necessary.

## Running the Server

1. **Navigate to the Server Directory:**

    ```bash
    cd src
    ```

2. **Start the WebSocket Server:**

    ```bash
    python server.py
    ```

    The server will start running on `ws://localhost:6789`.

3. **Start the Flask API Server:**

    In a new terminal window, navigate to the server directory:

    ```bash
    cd .\src\UsersAuthentication\api_sign  
    python api_server.py
    ```

    The Flask server will start running on `http://localhost:5000`.

## Connecting Clients

1. **Open the `welcome.html` File in a Browser:**

    Open the `welcome.html` file in a web browser to access the chat application interface.

2. **Sign Up and Sign In:**

    - Sign up for a new account using the sign-up form.
    - Sign in using the credentials you created.

## Using the Chat Application

1. **Creating a Group Chat:**

    - Click on the "Create Group Chat" button.
    - Enter the group name and select users to add to the group.
    - Click "Create" to create the group chat.

2. **Joining a Group Chat:**

    - Browse the list of available group chats.
    - Click on the desired group chat to join.

3. **Sending Messages:**

    - Enter your message in the input field and press Enter or click the send button to send a message.
    - Messages will be displayed in the chat window.

4. **Private Messaging:**

    - Search for a user using the search bar.
    - Click on the user to initiate a private chat.
    - Enter your message and press Enter or click the send button to send a private message.

5. **Persistent User Display:**

    The selected user will remain displayed on the dashboard for easy access in future sessions.

## Additional Information

- **User Interface:** The chat application has a simple and intuitive user interface. Navigate through different sections using the menu.
- **Error Handling:** Basic error handling is implemented to ensure a smooth user experience.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.
