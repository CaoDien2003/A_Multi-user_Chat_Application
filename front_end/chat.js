$(document).ready(function() {
    var socket;
    var token = localStorage.getItem('token'); // Retrieve the token stored during sign-in
    var currentChatUser;
    var localUserPhone = localStorage.getItem('userPhone'); // Retrieve the user's phone number
    var currentRoom;
    var receiverName;

    function connectWebSocket() {
        socket = new WebSocket('ws://localhost:6789');

        socket.onopen = function() {
            console.log('Connected to the WebSocket server.');
            socket.send(JSON.stringify({ action: 'authenticate', token: token }));
        };

        socket.onmessage = function(event) {
            var data = JSON.parse(event.data);
            console.log('Message from server:', data);
            if (data.type === 'system') {
                alert(data.message);
                if (data.message === 'Authentication successful') {
                    localStorage.setItem('userPhone', data.userPhone);
                    localUserPhone = data.userPhone;
                    console.log(`Authentication successful, userPhone set to ${localUserPhone}`);
                } else if (data.message.includes('has joined the room')) {
                    console.log('User joined the room:', data.message);
                } 
            } else if (data.type === 'chat' || data.type === 'private_chat') {
                addMessage(data.message, data.sender_name || data.sender, 'incoming');
                console.log(`Received message from ${data.sender_name || data.sender}: ${data.message}`);
            }
        };        
        
        socket.onclose = function() {
            console.log('Disconnected from the WebSocket server.');
        };

        socket.onerror = function(error) {
            console.log('WebSocket error:', error);
        };
    }

    async function sendMessage() {
        var input = document.getElementById('messageInput');
        if (input.value.trim() !== '') {
            var senderPhone = localUserPhone;
            var room = currentRoom;
    
            if (!room || !senderPhone) {
                console.log('Missing room or sender information.');
                console.log('Room:', room);
                console.log('Sender Phone:', senderPhone);
                return;
            }
    
            console.log(`Preparing to send message from ${senderPhone} to all users in room ${room}`);
    
            // Fetch the sender's name from the server
            let response = await fetch(`http://localhost:5000/get_user_by_phone?phone=${senderPhone}`);
            let userData = await response.json();
    
            if (!userData || !userData.name) {
                console.log('Failed to retrieve user name.');
                return;
            }
    
            var senderName = userData.name;
    
            // Send a broadcast message to the entire room
            socket.send(JSON.stringify({
                action: 'message',
                sender_name: senderName,
                room: room,
                message: input.value
            }));
    
            console.log(`Sent message from ${senderName} to all users in room ${room}: ${input.value}`);
            addMessage(input.value, 'You', 'outgoing');
            input.value = '';  // Clear the input after sending
        } else {
            console.log('No message to send');
        }
    }              

    function addMessage(msg, user, type) {
        var messages = document.getElementById('messages');
        var msgDiv = document.createElement('div');
        msgDiv.className = type === 'incoming' ? 'd-flex justify-content-start mb-4' : 'd-flex justify-content-end mb-4';
    
        msgDiv.innerHTML = `
            <div class="img_cont_msg">
                <img src="https://static.turbosquid.com/Preview/001292/481/WV/_D.jpg" class="rounded-circle user_img_msg">
            </div>
            <div class="msg_cotainer${type === 'incoming' ? '' : '_send'}">
                <span class="msg_user">${user}</span>
                ${msg}
                <span class="msg_time${type === 'incoming' ? '' : '_send'}">${new Date().toLocaleTimeString()}, Today</span>
            </div>`;
        messages.appendChild(msgDiv);
    }

    function clearMessages() {
        var messages = document.getElementById('messages');
        messages.innerHTML = '';
    }

    document.getElementById('send').addEventListener('click', function() {
        sendMessage();
    });

    document.getElementById('messageInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    $('#searchInput').on('input', function() {
        var query = $(this).val();
        if (query.trim() !== '') {
            $.ajax({
                url: 'http://localhost:5000/search_users',
                type: 'GET',
                data: { query: query },
                success: function(response) {
                    console.log('Search users response:', response); // Debugging log
                    displaySearchResults(response);
                },
                error: function(xhr, status, error) {
                    console.error('Search failed', xhr.responseJSON ? xhr.responseJSON.message : error);
                }
            });            
        } else {
            $('#searchResults').empty();
        }
    });

    function displaySearchResults(users) {
        var results = $('#searchResults');
        results.empty();
        users.forEach(user => {
            var userItem = `<li class="d-flex bd-highlight search-result" data-phone="${user.phone}" data-name="${user.name}">
                                <div class="user_info">
                                    <span>${user.name}</span>
                                    <p>${user.phone}</p>
                                </div>
                            </li>`;
            results.append(userItem);
        });
    
        $('.search-result').click(function() {
            var userPhone = $(this).data('phone');
            var userName = $(this).data('name');
            console.log(`User ${userPhone} clicked for private chat.`);
            initiatePrivateChat(userPhone, userName);
            
            // Hide search results and clear the search input
            $('#searchInput').val('');
            $('#searchResults').empty();
        });
    }
    
    $('#searchUserInput').on('input', function() {
        var query = $(this).val();
        if (query.trim() !== '') {
            $.ajax({
                url: 'http://localhost:5000/search_users',
                type: 'GET',
                data: { query: query },
                success: function(response) {
                    console.log('Search users response:', response); // Debugging log
                    displayUserSearchResults(response);
                },
                error: function(xhr, status, error) {
                    console.error('Search failed', xhr.responseJSON ? xhr.responseJSON.message : error);
                }
            });
        } else {
            $('#userSearchResults').empty();
        }
    });

    function displayUserSearchResults(users) {
        var results = $('#userSearchResults');
        results.empty();
        users.forEach(user => {
            var userItem = `<li class="d-flex bd-highlight user-search-result" data-phone="${user.phone}">
                                <div class="user_info">
                                    <span>${user.name}</span>
                                    <p>${user.phone}</p>
                                </div>
                            </li>`;
            results.append(userItem);
        });

        $('.user-search-result').click(function() {
            var userPhone = $(this).data('phone');
            console.log(`User ${userPhone} clicked for adding to group.`);
            var currentUsers = $('#groupUsers').val().split(',').map(user => user.trim());
            if (!currentUsers.includes(userPhone)) {
                currentUsers.push(userPhone);
                $('#groupUsers').val(currentUsers.join(', '));
            }
            
            // Hide search results and clear the search input
            $('#searchUserInput').val('');
            $('#userSearchResults').empty();
        });
    }

    function generateRoomName(...users) {
        return users.sort().join('_');
    }

    function initiatePrivateChat(userPhone, userName) {
        clearMessages();  // Clear previous messages
        currentChatUser = userPhone;
        $('#chatRoomName').text(userName);  // Set to the username
        var room = generateRoomName(localUserPhone, userPhone);
    
        console.log(`Initiating private chat with ${userPhone} (${userName}). Room: ${room}`);
        console.log(`Current chat user set to ${currentChatUser}`);
        console.log(`Local user: ${localUserPhone}`);
        currentRoom = room;
    
        socket.send(JSON.stringify({ action: 'create_room', room: room }));
        socket.send(JSON.stringify({ action: 'join_room', username: localUserPhone, room: room }));
    }
       
    function joinRoom(roomName) {
        clearMessages();  // Clear previous messages
        currentRoom = roomName;  // Set the current chat room to the selected room
        currentChatUser = null;  // Invalidate the currentChatUser for group chat
        $('#chatRoomName').text(roomName);
    
        console.log(`Joining room: ${roomName}`);
        console.log(`Local user: ${localUserPhone}`);
    
        socket.send(JSON.stringify({ action: 'join_room', username: localUserPhone, room: roomName }));
    }

    // Group chat creation event handlers
    $('#createGroupBtn').click(function() {
        var groupName = $('#groupName').val().trim();
        var groupUsers = $('#groupUsers').val().trim().split(',').map(user => user.trim());
        var localUserPhone = localStorage.getItem('userPhone'); // Get the current user's phone
    
        // Remove any empty entries
        groupUsers = groupUsers.filter(user => user !== '');
    
        if (groupName && groupUsers.length > 0) {
            if (!groupUsers.includes(localUserPhone)) {
                groupUsers.push(localUserPhone); // Add the current user to the list
            }
            var roomName = groupName;  // Use groupName as the room name directly
    
            console.log(`Creating group chat with name: ${groupName}, Users: ${groupUsers}`);
            // Send room creation request to the Flask server to save it in the database
            $.ajax({
                url: 'http://localhost:5000/create_room',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ room_name: roomName, users: groupUsers }),
                success: function(response) {
                    console.log('Room created:', response);
                    socket.send(JSON.stringify({
                        action: 'create_group_chat',
                        groupName: groupName,
                        users: groupUsers,
                        room: roomName
                    }));
                    $('#createGroupChatModal').modal('hide');
                },
                error: function(xhr, status, error) {
                    console.error('Room creation failed', xhr.responseJSON ? xhr.responseJSON.message : error);
                }
            });
        } else {
            alert('Please enter a group name and at least one user.');
        }
    });        

    // Search for rooms
    $('#searchRoomInput').on('input', function() {
        var query = $(this).val();
        var token = localStorage.getItem('token'); // Get the token from localStorage
        if (query.trim() !== '') {
            $.ajax({
                url: 'http://localhost:5000/search_rooms',
                type: 'GET',
                data: { query: query, token: token },
                success: function(response) {
                    console.log('Search rooms response:', response); // Debugging log
                    displayRoomSearchResults(response);
                },
                error: function(xhr, status, error) {
                    console.error('Search failed', xhr.responseJSON ? xhr.responseJSON.message : error);
                }
            });
        } else {
            $('#roomSearchResults').empty();
        }
    });

    function displayRoomSearchResults(rooms) {
        var results = $('#roomSearchResults');
        results.empty();
        rooms.forEach(room => {
            var roomItem = `<li class="d-flex bd-highlight room-search-result" data-name="${room.name}">
                                <div class="user_info">
                                    <span>${room.name}</span>  <!-- Use display_name here -->
                                </div>
                            </li>`;
            results.append(roomItem);
        });
    
        $('.room-search-result').click(function() {
            var roomName = $(this).data('name');
            console.log(`Room ${roomName} clicked for joining.`);
            joinRoom(roomName);
    
            // Hide search results and clear the search input
            $('#searchRoomInput').val('');
            $('#roomSearchResults').empty();
        });
    }

    connectWebSocket(); // Connect to WebSocket when the chat page loads
});
