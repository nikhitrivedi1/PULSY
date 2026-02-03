/**
 * Controller Layer - Request Handler for User Operations
 * 
 * Acts as the intermediary between routes and the model layer.
 * Responsible for:
 * - Delegating business logic to Model
 * - Handling request/response flow
 * - Coordinating between multiple model operations
 * 
 * @module controller
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { Model } from '../services/model.js';

// Get directory path for ES modules
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
     * Retrieve user's profile information
     * @param {string} username - User's username
     * @returns {Object} User profile data
     */
    getUserProfile(username) {
        console.log("Controller - Username: ", username);
        return this.model.getUserProfile(username);
    }

    /**
     * Add a preference to user's profile
     * @param {string} username - User's username
     * @param {string} preference - Preference to add
     * @returns {Promise<object>} Success status and updated preferences
     */
    addUserPreference(username, preference) {
        return this.model.addUserPreference(username, preference);
    }

    /**
     * Remove a preference from user's profile
     * @param {string} username - User's username
     * @param {string} preference - Preference to remove
     * @returns {Promise<object>} Success status and updated preferences
     */
    deleteUserPreference(username, preference) {
        return this.model.deleteUserPreference(username, preference);
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
     * @returns {Promise<Dictionary>} AI response to query
     * @returns {string} AI response to query
     * @returns {int} Log ID for the query
     */
    async chatQuery(query, username, user_history, ai_chat_history) {
        return await this.model.chatQuery(query, username, user_history, ai_chat_history);
    }

    /**
     * Process chat query with streaming responses via SSE
     * Returns an async generator that yields events as they arrive
     * 
     * @param {string} query - User's chat query
     * @param {string} username - User's username
     * @param {Array} user_history - History of user queries
     * @param {Array} ai_chat_history - History of AI responses
     * @returns {AsyncGenerator} Async generator yielding event objects
     */
    chatQueryStream(query, username, user_history, ai_chat_history) {
        return this.model.chatQueryStream(query, username, user_history, ai_chat_history);
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
     * Test connection to a user device using API key
     * @param {string} device_type - Type of device (e.g., "Oura Ring")
     * @param {string} api_key - API key for device
     * @returns {Promise<boolean>} True if device connection successful
     */
    testUserDevices(device_type, api_key) {
        return this.model.testUserDevices(device_type, api_key);
    }

    /**
     * Add a new device to user's account
     * @param {string} username - User's username
     * @param {string} device_type - Type of device
     * @param {string} device_name - Name of device
     * @param {string} api_key - API key for device
     * @returns {Promise<boolean>} Device addition success status
     */
    async addDevice(username, device_type, api_key) {
        return await this.model.addDevice(username, device_type, api_key);
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

    /**
     * Generate OAuth authorization URL for Oura Ring
     * @param {object} session - Express session object
     * @returns {string} Authorization URL for Oura Ring OAuth flow
     */
    authorizeOuraRingUser(session) {
        return this.model.authorizeOuraRingUser(session);
    }

    /**
     * Exchange OAuth authorization code for access/refresh tokens
     * @param {string} code - OAuth authorization code from Oura Ring
     * @returns {Promise<object>} Access and refresh tokens
     */
    getTokensOuraRing(code) {
        return this.model.getTokensOuraRing(code);
    }

    /**
     * Update stored OAuth tokens for a user's Oura Ring
     * @param {string} username - User's username
     * @param {object} tokens - New access and refresh tokens
     * @returns {Promise<object>} Success status
     */
    updateTokensOuraRing(username, tokens) {
        return this.model.updateTokensOuraRing(username, tokens);
    }

    /**
     * Refresh expired OAuth tokens for user's Oura Ring
     * @param {string} username - User's username
     * @returns {Promise<object>} New tokens or error
     */
    refreshOuraTokens(username) {
        return this.model.refreshOuraTokens(username);
    }

    /**
     * Add user feedback for an AI response
     * @param {number} log_id - ID of the logged message
     * @param {string} feedback - "up" or "down" for thumbs up/down
     * @param {string} comment - Optional text feedback
     * @returns {Promise<object>} Success status
     */
    addFeedback(log_id, feedback, comment) {
        return this.model.addFeedback(log_id, feedback, comment);
    }

    /**
     * Retrieve username associated with OAuth state
     * @param {string} state - OAuth state string
     * @returns {Promise<object>} Username or error
     */
    getSession(state) {
        return this.model.getSession(state);
    }

    /**
     * Delete OAuth state mapping after completion
     * @param {string} state - OAuth state string
     * @returns {Promise<object>} Success status
     */
    deleteSession(state) {
        return this.model.deleteSession(state);
    }

    /**
     * Save chat history for a user to database
     * @param {string} username - User's username
     * @param {string} query - User's query
     * @param {string} response - AI response
     * @param {number|null} logId - Log ID for feedback tracking
     * @returns {Promise<object>} Success status
     */
    saveChatHistory(username, query, response, logId) {
        return this.model.saveChatHistory(username, query, response, logId);
    }

    /**
     * Get chat history for a user from database
     * @param {string} username - User's username
     * @returns {Promise<object>} Chat history with queries and responses arrays
     */
    getChatHistory(username) {
        return this.model.getChatHistory(username);
    }

    /**
     * Clear chat history for a user
     * @param {string} username - User's username
     * @returns {Promise<object>} Success status
     */
    clearChatHistory(username) {
        return this.model.clearChatHistory(username);
    }

}

export { Controller };