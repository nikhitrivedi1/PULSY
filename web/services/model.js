import fs from 'fs';
import {dirname, join} from 'path';
import { fileURLToPath } from 'url';

/**
 * Model class handling user authentication and data management
 */
class Model {
    /**
     * Initialize Model with database path and data
     * @constructor
     */
    constructor() {
        this.db_path = join(dirname(fileURLToPath(import.meta.url)), "../../shared/user_state.json");
        this.data = JSON.parse(fs.readFileSync(this.db_path, 'utf8'));
    }

    /**
     * Authenticate user credentials
     * @param {string} username - User's username
     * @param {string} password - User's password
     * @returns {boolean} True if authentication successful, false otherwise
     */
    authenticate(username, password) {
        return this.data[username]["password"] === password;
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
        if (this.checkDuplicate(username)) {
            console.log("User already exists");
            return false;
        }

        this.data[username] = {
            password: password,
            profile: profile,
            goals: {},
            preferences: [preferences],
            devices: {}
        };

        try {
            fs.writeFileSync(this.db_path, JSON.stringify(this.data, null, 2), 'utf8');
            return true;
        } catch (error) {
            console.error('Error writing to file:', error);
            return false;
        }
    }

    /**
     * Check if username already exists
     * @param {string} username - Username to check
     * @returns {boolean} True if username exists, false otherwise
     */
    checkDuplicate(username) {
        return this.data[username] !== undefined;
    }

    /**
     * Get user's connected devices
     * @param {string} username - User's username
     * @returns {Object} User's devices
     */
    getUserDevices(username) {
        return this.data[username]["devices"];
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
            body: JSON.stringify({device_type: device_object["device_type"], device_name: device_object["device_name"], api_key: device_object["api_key"]})
        });

        if (response.status == 200){
            let data = await response.json();
            return data;
        }
        let error_message = await response.json()
        throw new Error("Status: " + response.status + " Error: " + error_message["detail"])
    }

    /**
     * Load user's health and fitness goals
     * @param {string} username - User's username
     * @returns {Promise<Object>} User's goals
     */
    async loadUserGoals(username) {
        let response = await fetch(`http://0.0.0.0:8000/load_user_goals/${username}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
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
        return this.data[username]["profile"];
    }

    /**
     * Update user's profile information
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
     * Add a new device for a user
     * @param {string} username - User's username
     * @param {string} device_type - Type of device
     * @param {string} device_name - Name of device
     * @param {string} api_key - Device API key
     * @returns {Promise<boolean>} True if device added successfully, false otherwise
     */
    async addDevice(username, device_type, device_name, api_key) {
        let device = {
            "device_type": device_type,
            "device_name": device_name,
            "api_key": api_key
        }

        this.data[username]["devices"].push(device);

        try {
            fs.writeFileSync(this.db_path, JSON.stringify(this.data, null, 2), 'utf8');
            return true;
        } catch (error) {
            console.error('Error writing to file:', error);
            return false;
        }
    }

    /**
     * Delete a device for a user
     * @param {string} username - User's username
     * @param {string} device_name - Name of device to delete
     * @returns {Promise<boolean>} True if device deleted successfully, false otherwise
     */
    async deleteDevice(username, device_name) {
        this.data[username]["devices"] = this.data[username]["devices"].filter(device => device["device_name"] !== device_name);

        try {
            fs.writeFileSync(this.db_path, JSON.stringify(this.data, null, 2), 'utf8');
            return true;
        } catch (error) {
            console.error('Error writing to file:', error);
            return false;
        }
    }

    /**
     * Edit device information for a user
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
        let response = await fetch('http://0.0.0.0:8000/query/', {
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
}

export { Model };