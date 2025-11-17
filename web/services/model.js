import fs from 'fs';
import {dirname, join} from 'path';
import { fileURLToPath } from 'url';
import UserDbOperations from './postgres_ops.js';
import {GoogleAuth} from 'google-auth-library';

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
            "client_id": "b4bb9677-f948-4813-bd45-098fff51a7a5",
            "client_secret": "42EWT2UsPjXU4B3LwAcB2WwurCg2ng1YWO5PAzH0QQY",
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

    authorizeOuraRingUser(){
        const CLIENT_ID = 'b4bb9677-f948-4813-bd45-098fff51a7a5';
        const REDIRECT_URI = "http://localhost:3000/my_devices/authorize_oura_ring";
        const scopes = ["personal", "daily", 'heartrate', 'stress', 'workout', 'spo2Daily'];
      
        const authUrl = `https://cloud.ouraring.com/oauth/authorize?` +
          `client_id=${CLIENT_ID}&` +
          `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
          `response_type=code&` +
          `scope=${scopes.join(" ")}`;
        
        console.log("Auth URL: ", authUrl);
      
        return authUrl;
    }

    async getTokensOuraRing(code) {
        const CLIENT_ID = 'b4bb9677-f948-4813-bd45-098fff51a7a5';
        const REDIRECT_URI = "http://localhost:3000/my_devices/authorize_oura_ring";

        const response = await fetch("https://api.ouraring.com/oauth/token", {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
              grant_type: "authorization_code",
              code: code,
              client_id: CLIENT_ID,
              client_secret: '42EWT2UsPjXU4B3LwAcB2WwurCg2ng1YWO5PAzH0QQY',
              redirect_uri: REDIRECT_URI
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
            'client_id': 'b4bb9677-f948-4813-bd45-098fff51a7a5',
            'client_secret': '42EWT2UsPjXU4B3LwAcB2WwurCg2ng1YWO5PAzH0QQY'
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
        // Get the Google Auth token
        const targetAudience = process.env.BACKEND_URL;

        const client = new GoogleAuth();
        const idTokenClient = await client.getIdTokenClient(targetAudience);

        const url = `${process.env.BACKEND_URL}/query/`;


        let response = await idTokenClient.fetch(url, {
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
    }

    /**
     * Get user's profile information 
     * @param {string} username - User's username
     * @returns {Object} User profile data
     */
    getUserProfile(username) {
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