import fs from 'fs';
import UserDbOperations from './postgres_ops.js';
import crypto from 'crypto';
import { GoogleAuth } from "google-auth-library";

/**
 * Model class handling user authentication and data management
 */
class Model {
    /**
     * Initialize Model with database path and data
     * @constructor
     */
    constructor() {
        // This will be removed in the future
        // this.db_path = join(dirname(fileURLToPath(import.meta.url)), "../../shared/user_state.json");
        // this.data = JSON.parse(fs.readFileSync(this.db_path, 'utf8'));
        // Initialize the PostGreSQL database connection
        this.user_db_operations = new UserDbOperations();
    }

    /**
     * Authenticate user credentials
     * @param {string} username - User's username
     * @param {string} password - User's password
     * @returns {boolean} True if authentication successful, false otherwise
     */
    authenticate(username, password) {
        // get user password from the database
        return this.user_db_operations.verifyPassword(password, username);
    }

    async refreshTokens(username) {
        let refresh_token = await this.user_db_operations.refreshTokens(username);
        if (refresh_token.success) {
            let tokens = await this.ouraRingRefreshCall(refresh_token.return_value);
            if (tokens.success) {
                return { success: true, return_value: tokens.return_value };
            } else {
                return { success: false, return_value: tokens.return_value };
            }
        }
        return { success: false, return_value: refresh_token.return_value };
    }

    async ouraRingRefreshCall(refresh_token) {
        let token_data = {
            "refresh_token": refresh_token,
            "client_id": process.env.OURA_CLIENT_ID,
            "client_secret": process.env.OURA_SECRET,
            "grant_type": "refresh_token"
        }
        const response = await fetch("https://api.ouraring.com/oauth/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams(token_data)
        });
        console.log("Response: ", response)

        // Upload the nwe tokens to the data base
        if (response.status == 200) {
            let tokens = await response.json();
            return this.user_db_operations.updateTokensOuraRing(username, tokens);
        } else {
            return { success: false, return_value: response.json() };
        }
    }

    /**
     * Add a new user to the system
     * @param {string} username - New user's username
     * @param {string} password - New user's password
     * @param {Object} profile - User profile information
     * @param {Object} preferences - User preferences
     * @returns {boolean} True if user added successfully, false otherwise
     */
    addUser(username, password, profile, preferences) {
        // if (this.checkDuplicate(username)) {
        //     console.log("User already exists");
        //     return false;
        // }
        // TODO: Need to add a check to see if the user already exists

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

    getSession(state) {
        return this.user_db_operations.getSession(state);
    }

    async deleteSession(state) {
        console.log("Deleting Session: ", state);
        return await this.user_db_operations.deleteSession(state);
    }

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

    updateTokensOuraRing(username, tokens) {
        return this.user_db_operations.updateTokensOuraRing(username, tokens);
    }
    /**
     * Get user's connected devices
     * @param {string} username - User's username
     * @returns {Object} User's devices
     */
    getUserDevices(username) {
        return this.user_db_operations.getDeviceInformation(username);
    }

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
     * Refresh the access token for the Oura Ring
     * @param {string} refreshToken - The refresh token for the Oura Ring
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
     * Load metrics from a user device
     * @param {Object} device_object - Device information object
     * @param {string} device_object.device_type - Type of device
     * @param {string} device_object.device_name - Name of device
     * @param {string} device_object.api_key - Device API key
     * @returns {Promise<Object>} Device metrics data
     */
    async loadUserDevices(device_object) {
        let response = await fetch(`http://0.0.0.0:8000/load_user_devices/`, {
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
     * Add a new device for a user
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
     * Delete a device for a user
     * @param {string} username - User's username
     * @param {string} device_name - Name of device to delete
     * @returns {Promise<boolean>} True if device deleted successfully, false otherwise
     */
    async deleteDevice(username, device_type) {
        // TODO: Need to add error handling here
        return await this.user_db_operations.deleteDevice(username, device_type);
    }

    /**
     * Edit device information for a user - PERHAPS NOT NEEDED 
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
     * Process a chat query through the AI system
     * @param {string} query - User's query
     * @param {string} username - User's username
     * @param {Array} user_history - History of user queries
     * @param {Array} ai_chat_history - History of AI responses
     * @returns {Promise<Object|string>} AI response
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
            
            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(`Backend error: ${res.status} ${errorText}`);
            }
        
            return res.json();
        }
    }

    /**
     * Get user's profile information 
     * @param {string} username - User's username
     * @returns {Object} User profile data
     */
    getUserProfile(username) {
        console.log("Model - Username: ", username);
        return this.user_db_operations.getAgenticPreferences(username);
    }

    addUserPreference(username, preference) {
        return this.user_db_operations.addAgenticPreference(username, preference);
    }

    deleteUserPreference(username, preference) {
        return this.user_db_operations.removeAgenticPreference(username, preference);
    }

    /**
     * Update user's profile information - may just delete this function
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

    addFeedback(log_id, feedback, comment) {
        return this.user_db_operations.addFeedback(log_id, feedback, comment);
    }

}

export { Model };