/**
 * Model Layer for User and Device Management
 * 
 * Handles business logic for:
 * - User authentication and registration
 * - OAuth flows (Oura Ring integration)
 * - Device management (add, delete, test connections)
 * - Communication with backend AI agent
 * - User preferences and feedback
 * 
 * Acts as an intermediary between controllers and database operations
 * 
 * @module model
 */

import fs from 'fs';
import UserDbOperations from './postgres_ops.js';
import crypto from 'crypto';
import { GoogleAuth } from "google-auth-library";

/**
 * Model class handling user authentication and data management
 * Provides high-level business logic methods for the application
 */
class Model {
    /**
     * Constructs a new Model object and initializes the database operations.
     * @constructor
     */
    constructor() {
        // Initialize the PostgreSQL database connection
        this.user_db_operations = new UserDbOperations();
    }

    /**
     * Authenticates user credentials.
     * @param {string} username - User's username
     * @param {string} password - User's password
     * @returns {boolean} True if authentication successful, false otherwise
     */
    authenticate(username, password) {
        // Get user password from the database
        return this.user_db_operations.verifyPassword(password, username);
    }

    /**
     * Refreshes OAuth tokens for a user's Oura Ring integration.
     * @param {string} username - User's username
     * @returns {Promise<object>} Success status and new tokens or error
     */
    async refreshOuraTokens(username) {
        // Step 1: Get the refresh token from the database
        let refresh_token_result = await this.user_db_operations.getRefreshToken(username);
        if (!refresh_token_result.success) {
            return { success: false, return_value: refresh_token_result.return_value };
        }

        // Step 2: Call Oura API to exchange refresh token for new tokens
        let tokens_result = await this.ouraRingRefreshCall(refresh_token_result.return_value, username);
        if (!tokens_result.success) {
            return { success: false, return_value: tokens_result.return_value };
        }

        return { success: true, return_value: tokens_result.return_value };
    }

    /**
     * Makes an API call to Oura Ring to refresh the access token.
     * @param {string} refresh_token - The refresh token from Oura
     * @param {string} username - User's username for storing new tokens
     * @returns {Promise<object>} New access/refresh tokens or error
     * @private
     */
    async ouraRingRefreshCall(refresh_token, username) {
        let token_data = {
            "refresh_token": refresh_token,
            "client_id": process.env.OURA_CLIENT_ID,
            "client_secret": process.env.OURA_SECRET,
            "grant_type": "refresh_token"
        }

        try {
            const response = await fetch("https://api.ouraring.com/oauth/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams(token_data)
            });
            console.log("Oura token refresh response status:", response.status);

            if (response.status === 200) {
                // Parse the new tokens
                let tokens = await response.json();
                console.log("New tokens received from Oura API");

                // Save the new tokens to the database
                const update_result = await this.user_db_operations.updateTokensOuraRing(username, tokens);
                if (update_result.success) {
                    return { success: true, return_value: tokens };
                } else {
                    return { success: false, return_value: "Failed to save new tokens" };
                }
            } else {
                const error_body = await response.json();
                console.error("Oura token refresh failed:", error_body);
                return { success: false, return_value: error_body.error_description || "Token refresh failed" };
            }
        } catch (error) {
            console.error("Error calling Oura API:", error);
            return { success: false, return_value: error.message };
        }
    }

    /**
     * Registers a new user in the system.
     * @param {string} username - Chosen username
     * @param {string} password - User's password (will be hashed)
     * @param {object} profile - User profile data (first_name, last_name)
     * @param {array} preferences - User preferences array
     * @returns {Promise<object>} Success status with user ID or error
     */
    addUser(username, password, profile, preferences) {
        let user_data = {
            username: username,
            password: password,
            preferences: preferences,
            devices: {},
            first_name: profile.first_name,
            last_name: profile.last_name
        };
        return this.user_db_operations.uploadUserData(user_data);
    }

    /**
     * Generates an OAuth authorization URL for the Oura Ring integration.
     * Stores the state and session for CSRF protection.
     * @param {string} session - Session or unique identifier to map state to user/session
     * @returns {string} The OAuth URL for user authorization
     */
    authorizeOuraRingUser(session){
        const scopes = ["personal", "daily", 'heartrate', 'stress', 'workout', 'spo2Daily'];

        // Generate state and store state: user in SQL DB
        const state = crypto.randomBytes(16).toString("hex");
        this.user_db_operations.storeState(state, session);
      
        const authUrl = `https://cloud.ouraring.com/oauth/authorize?` +
          `client_id=${process.env.OURA_CLIENT_ID}&` +
          `redirect_uri=${encodeURIComponent(process.env.REDIRECT_URI)}&` +
          `response_type=code&` +
          `scope=${scopes.join(" ")}&` +
          `state=${state}`;      
        return authUrl;
    }

    /**
     * Retrieves a session by state value, for OAuth flows.
     * @param {string} state - The state string used for OAuth session validation
     * @returns {Object} Session data
     */
    getSession(state) {
        return this.user_db_operations.getSession(state);
    }

    /**
     * Deletes a session given a state value.
     * @param {string} state - The state string for the session
     * @returns {Promise<Object>} Result of the deletion
     */
    async deleteSession(state) {
        console.log("Deleting Session: ", state);
        return await this.user_db_operations.deleteSession(state);
    }

    /**
     * Fetches Oura Ring tokens using authorization code from OAuth flow.
     * @param {string} code - OAuth token code
     * @returns {Promise<Object>} Tokens received from Oura Ring
     */
    async getTokensOuraRing(code) {
        const response = await fetch("https://api.ouraring.com/oauth/token", {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
              grant_type: "authorization_code",
              code: code,
              client_id: process.env.OURA_CLIENT_ID,
              client_secret: process.env.OURA_SECRET,
              redirect_uri: process.env.REDIRECT_URI
            })
        });
        const tokens = await response.json();
        return tokens;
    }

    /**
     * Updates tokens for the Oura Ring device for a user.
     * @param {string} username - User's username
     * @param {Object} tokens - Oura Ring tokens to store
     * @returns {Promise<object>} Result of the update operation
     */
    updateTokensOuraRing(username, tokens) {
        return this.user_db_operations.updateTokensOuraRing(username, tokens);
    }

    /**
     * Retrieves a user's connected device information.
     * @param {string} username - User's username
     * @returns {Object} User's device information or devices list
     */
    getUserDevices(username) {
        return this.user_db_operations.getDeviceInformation(username);
    }

    /**
     * Tests if a given device type and API key are connected and valid.
     * Only supports Oura Ring currently.
     * @param {string} device_type - Device type (e.g., "Oura Ring")
     * @param {string} api_key - API key/token for the device
     * @returns {Promise<boolean>} True if the device is valid/connected, false otherwise
     */
    async testUserDevices(device_type, api_key) {
        // Make call directly to device API to test if the device is connected
        if (device_type == "Oura Ring"){
            const endpoint = "usercollection/personal_info";
            try {
                let response = await fetch(`https://api.ouraring.com/v2/${endpoint}`, {
                headers: {
                    'Authorization': `Bearer ${api_key}`
                }
                });
                console.log("Response: ", response)

                if (response.status == 200){
                    return true;
                } 
            }catch (error) {
                console.error('Error testing device:', error);
                return false;
            }
        }
        return false;
    }

    /**
     * Refreshes the access token for the Oura Ring device.
     * @param {string} refreshToken - The refresh token for Oura Ring
     * @returns {Promise<Object>} The response from the Oura Ring API
     */
    async refreshAccessToken(refreshToken) {
        const response = await fetch('https://api.ouraring.com/oauth/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({
            'grant_type': 'refresh_token',
            'refresh_token': refreshToken,
            'client_id': process.env.OURA_RING_CLIENT_ID,
            'client_secret': process.env.OURA_SECRET,
          })
        });
      
        return response.json();
    }

    /**
     * Loads metrics and data from a user device using its information object.
     * @param {Object} device_object - Device information object
     * @param {string} device_object.device_type - Type of device
     * @param {string} device_object.device_name - Name of device
     * @param {string} device_object.api_key - Device API key
     * @returns {Promise<Object>} Device metrics data or throws error if fails
     */
    async loadUserDevices(device_object) {
        let response = await fetch(process.env.BACKEND_URL + "/load_user_devices/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({device_type: device_object["device_type"], api_key: device_object["api_key"]})
        });

        if (response.status == 200){
            let data = await response.json();
            return data;
        }
        let error_message = await response.json()
        throw new Error("Status: " + response.status + " Error: " + error_message["detail"])
    }

    /**
     * Adds a new device for a user.
     * @param {string} username - User's username
     * @param {string} device_type - Type of device
     * @param {string} api_key - Device API key
     * @returns {Promise<boolean>} True if device added successfully, false otherwise
     */
    async addDevice(username, device_type, api_key) {
        let device = {
            "device_type": device_type,
            "api_key": api_key
        }
        // TODO: Need to add error handling here
        return await this.user_db_operations.addDevice(username, device);
    }

    /**
     * Deletes a device for a user.
     * @param {string} username - User's username
     * @param {string} device_type - Type of device to delete
     * @returns {Promise<boolean>} True if device deleted successfully, false otherwise
     */
    async deleteDevice(username, device_type) {
        // TODO: Need to add error handling here
        return await this.user_db_operations.deleteDevice(username, device_type);
    }

    /**
     * Edits device information for a user. (Legacy, uses file-based storage.)
     * @param {string} username - User's username
     * @param {string} old_device_name - Current device name
     * @param {string} new_device_name - New device name
     * @param {string} device_type - Updated device type
     * @param {string} api_key - Updated API key
     * @returns {boolean} True if device edited successfully, false otherwise
     */
    editDevice(username, old_device_name, new_device_name, device_type, api_key) {
        this.data[username]["devices"] = this.data[username]["devices"].map(device => 
            device["device_name"] === old_device_name ? 
            { ...device, device_name: new_device_name, device_type: device_type, api_key: api_key } : 
            device
        );

        try {
            fs.writeFileSync(this.db_path, JSON.stringify(this.data, null, 2), 'utf8');
            return true;
        } catch (error) {
            console.error('Error writing to file:', error);
            return false;
        }
    }

    /**
     * Processes a chat query through the AI system.
     * This handles local and deployed (Google Auth) execution.
     * @param {string} query - User's query
     * @param {string} username - User's username
     * @param {Array} user_history - History of user queries
     * @param {Array} ai_chat_history - History of AI responses
     * @returns {Promise<Object|string>} AI response or an error string
     */
    async chatQuery(query, username, user_history, ai_chat_history) {
        const url = `${process.env.BACKEND_URL}/query/`;

        if (process.env.LOCAL_MODE == "true"){

            let response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({query: query, username: username, user_history: user_history, ai_chat_history: ai_chat_history })
            });

            if (response instanceof String){
                return response
            }
            return response.json();
        } else {
            // Get the Google Auth Token
            const auth = new GoogleAuth()
            const client = await auth.getIdTokenClient(process.env.BACKEND_URL)

            const res = await client.request({
                url: url,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({query: query, username: username, user_history: user_history, ai_chat_history: ai_chat_history })
            })
            
            // GoogleAuth client.request() automatically parses the response
            // The data is available in res.data, not res.json()
            return res.data;
        }
    }

    /**
     * Processes a chat query with streaming responses via SSE.
     * Returns an async generator that yields events as they arrive.
     * 
     * @param {string} query - User's query
     * @param {string} username - User's username
     * @param {Array} user_history - History of user queries
     * @param {Array} ai_chat_history - History of AI responses
     * @returns {AsyncGenerator} Async generator yielding event objects
     */
    async *chatQueryStream(query, username, user_history, ai_chat_history) {
        // Build query parameters for SSE GET request
        const params = new URLSearchParams({
            query: query,
            username: username,
            user_history: JSON.stringify(user_history),
            ai_chat_history: JSON.stringify(ai_chat_history)
        });
        
        const url = `${process.env.BACKEND_URL}/query/stream?${params.toString()}`;

        if (process.env.LOCAL_MODE === "true") {
            // Local mode: direct fetch with SSE
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'text/event-stream'
                }
            });

            if (!response.ok) {
                yield { type: 'error', message: `Backend error: ${response.status}` };
                return;
            }

            // Read the SSE stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            try {
                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) break;
                    
                    // Decode the chunk and add to buffer
                    buffer += decoder.decode(value, { stream: true });
                    
                    // Process complete SSE messages (lines ending with \n\n)
                    const lines = buffer.split('\n\n');
                    buffer = lines.pop() || ''; // Keep incomplete line in buffer
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonStr = line.slice(6); // Remove 'data: ' prefix
                                const event = JSON.parse(jsonStr);
                                yield event;
                            } catch (parseError) {
                                console.error('Error parsing SSE event:', parseError, line);
                            }
                        }
                    }
                }
                
                // Process any remaining buffer
                if (buffer.startsWith('data: ')) {
                    try {
                        const jsonStr = buffer.slice(6);
                        const event = JSON.parse(jsonStr);
                        yield event;
                    } catch (parseError) {
                        // Incomplete message, ignore
                    }
                }
            } finally {
                reader.releaseLock();
            }
        } else {
            // Deployed mode with Google Auth
            // Note: SSE with Google Auth is more complex - we need to use regular request
            // and parse the streaming response
            const auth = new GoogleAuth();
            const client = await auth.getIdTokenClient(process.env.BACKEND_URL);
            
            // Get the auth token
            const headers = await client.getRequestHeaders();
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    ...headers,
                    'Accept': 'text/event-stream'
                }
            });

            if (!response.ok) {
                yield { type: 'error', message: `Backend error: ${response.status}` };
                return;
            }

            // Read the SSE stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            try {
                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    
                    const lines = buffer.split('\n\n');
                    buffer = lines.pop() || '';
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonStr = line.slice(6);
                                const event = JSON.parse(jsonStr);
                                yield event;
                            } catch (parseError) {
                                console.error('Error parsing SSE event:', parseError, line);
                            }
                        }
                    }
                }
                
                if (buffer.startsWith('data: ')) {
                    try {
                        const jsonStr = buffer.slice(6);
                        const event = JSON.parse(jsonStr);
                        yield event;
                    } catch (parseError) {
                        // Incomplete message, ignore
                    }
                }
            } finally {
                reader.releaseLock();
            }
        }
    }

    /**
     * Retrieves the user's profile information.
     * @param {string} username - User's username
     * @returns {Object} User profile data
     */
    getUserProfile(username) {
        console.log("Model - Username: ", username);
        return this.user_db_operations.getAgenticPreferences(username);
    }

    /**
     * Adds a user preference to the user's profile.
     * @param {string} username - User's username
     * @param {string} preference - Preference to add
     * @returns {Promise<Object>} Result of the add operation
     */
    addUserPreference(username, preference) {
        return this.user_db_operations.addAgenticPreference(username, preference);
    }

    /**
     * Deletes a user preference from the user's profile.
     * @param {string} username - User's username
     * @param {string} preference - Preference to remove
     * @returns {Promise<Object>} Result of the delete operation
     */
    deleteUserPreference(username, preference) {
        return this.user_db_operations.removeAgenticPreference(username, preference);
    }

    /**
     * Updates user's profile information (Legacy, file-based; probably unused).
     * @param {string} username - User's username
     * @param {Object} profile - Updated profile information
     * @returns {Object|Error} Updated profile or error if update fails
     */
    updateUserProfile(username, profile) {
        this.data[username]["profile"] = profile;
        
        try{
            fs.writeFileSync(this.db_path, JSON.stringify(this.data, null, 2), 'utf8');
            return profile;
        } catch (error) {
            console.error('Error writing to file:', error);
            return error;
        }
    }

    /**
     * Adds feedback for a log or user interaction.
     * @param {string} log_id - The log entry ID to associate feedback with
     * @param {string} feedback - Feedback content/label
     * @param {string} comment - Any additional user comments
     * @returns {Promise<Object>} Result of the feedback insertion
     */
    addFeedback(log_id, feedback, comment) {
        return this.user_db_operations.addFeedback(log_id, feedback, comment);
    }

    /**
     * Save chat history for a user (appends to existing history in DB)
     * @param {string} username - User's username
     * @param {string} query - User's query
     * @param {string} response - AI response
     * @param {number|null} logId - Log ID for feedback tracking
     * @returns {Promise<Object>} Result of the save operation
     */
    saveChatHistory(username, query, response, logId) {
        return this.user_db_operations.saveChatHistory(username, query, response, logId);
    }

    /**
     * Get chat history for a user from database
     * @param {string} username - User's username
     * @returns {Promise<Object>} Chat history with queries and responses arrays
     */
    getChatHistory(username) {
        return this.user_db_operations.getChatHistory(username);
    }

    /**
     * Clear chat history for a user (reset to empty)
     * @param {string} username - User's username
     * @returns {Promise<Object>} Result of the clear operation
     */
    clearChatHistory(username) {
        return this.user_db_operations.clearChatHistory(username);
    }

}

export { Model };