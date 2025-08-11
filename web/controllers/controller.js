// Import required libraries
import path from 'path';
import { fileURLToPath } from 'url';
import { Model } from '../services/model.js';

// Get directory path
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Controller Class for Authentication and User Management
 * Handles user authentication, profile management, and device interactions
 */
class Controller {
    /**
     * Initialize Controller with LoginModel instance
     */
    constructor() {
        this.model = new Model();
    }

    /**
     * Authenticate user credentials
     * @param {string} username - User's username
     * @param {string} password - User's password
     * @returns {boolean} Authentication success status
     */
    authenticate(username, password) {
        return this.model.authenticate(username, password);
    }

    /**
     * Create a new user account
     * @param {string} username - New user's username
     * @param {string} password - New user's password
     * @param {Object} profile - User profile information
     * @param {Object} preferences - User preferences
     * @returns {boolean} User creation success status
     */
    addUser(username, password, profile, preferences) {
        return this.model.addUser(username, password, profile, preferences);
    }

    /**
     * Load metrics from user's connected devices
     * @param {string} username - User's username
     * @returns {Promise<Array>} Array of metrics from user's devices
     */
    async loadUserMetrics(username) {
        let user_devices = this.model.getUserDevices(username);
        let device_metrics = [];
        if (user_devices.length > 0) {
            for (let device of user_devices) {
                    device_metrics.push(await this.model.loadUserDevices(device));
                }
        }
        return device_metrics;
    }

    /**
     * Load user's health and fitness goals
     * @param {string} username - User's username
     * @returns {Promise<Object>} User's goals
     */
    async loadUserGoals(username) {
        return await this.model.loadUserGoals(username);
    }

    /**
     * Retrieve user's profile information
     * @param {string} username - User's username
     * @returns {Object} User profile data
     */
    getUserProfile(username) {
        return this.model.getUserProfile(username);
    }

    /**
     * Update user's profile information
     * @param {string} username - User's username
     * @param {Object} profile - Updated profile information
     * @returns {Object} Updated user profile
     */
    updateUserProfile(username, profile) {
        return this.model.updateUserProfile(username, profile);
    }

    /**
     * Process chat query and return AI response
     * @param {string} query - User's chat query
     * @param {string} username - User's username
     * @param {Array} user_history - History of user queries
     * @param {Array} ai_chat_history - History of AI responses
     * @returns {Promise<string>} AI response to query
     */
    async chatQuery(query, username, user_history, ai_chat_history) {
        return await this.model.chatQuery(query, username, user_history, ai_chat_history);
    }

    /**
     * Get list of user's connected devices
     * @param {string} username - User's username
     * @returns {Array} List of user's devices
     */
    getUserDevices(username) {
        return this.model.getUserDevices(username);
    }

    /**
     * Add a new device to user's account
     * @param {string} username - User's username
     * @param {string} device_type - Type of device
     * @param {string} device_name - Name of device
     * @param {string} api_key - API key for device
     * @returns {Promise<boolean>} Device addition success status
     */
    async addDevice(username, device_type, device_name, api_key) {
        return await this.model.addDevice(username, device_type, device_name, api_key);
    }

    /**
     * Remove a device from user's account
     * @param {string} username - User's username
     * @param {string} device_name - Name of device to delete
     * @returns {Promise<boolean>} Device deletion success status
     */
    async deleteDevice(username, device_name) {
        return await this.model.deleteDevice(username, device_name);
    }

    /**
     * Edit existing device information
     * @param {string} username - User's username
     * @param {string} old_device_name - Current device name
     * @param {string} new_device_name - New device name
     * @param {string} device_type - Type of device
     * @param {string} api_key - API key for device
     * @returns {boolean} Device edit success status
     */
    editDevice(username, old_device_name, new_device_name, device_type, api_key) {
        return this.model.editDevice(username, old_device_name, new_device_name, device_type, api_key);
    }
}

export { Controller };