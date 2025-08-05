// Import required libraries
import path from 'path';
import { fileURLToPath } from 'url';
import { LoginModel } from '../services/login_model.js';

// Get directory path
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Login Controller Class for Authnetication and User Management
class LoginController {
    constructor() {
        this.loginModel = new LoginModel();
    }

    authenticate(username, password) {
        // Perform Authnetiction using model file   
        return this.loginModel.authenticate(username, password);;
    }

    // Functions for Adding a New User
    addUser(username, password, profile, preferences) {
        return this.loginModel.addUser(username, password, profile, preferences);
    }

    // Load the user's metrics from the database
    async loadUserMetrics(username) {
        // Query Database for User Devices
        let user_devices = this.loginModel.getUserDevices(username);
        console.log(user_devices);
        let device_metrics = [];
        for (let device of user_devices) {
            device_metrics.push(await this.loginModel.loadUserDevices(device));
        }
        return device_metrics;
    }

    async loadUserGoals(username) {
        return await this.loginModel.loadUserGoals(username);
    }

    getUserProfile(username) {
        return this.loginModel.getUserProfile(username);
    }

    updateUserProfile(username, profile) {
        return this.loginModel.updateUserProfile(username, profile);
    }

    async chatQuery(query, username, user_history, ai_chat_history) {
        return await this.loginModel.chatQuery(query, username, user_history, ai_chat_history);
    }


    getUserDevices(username) {
        return this.loginModel.getUserDevices(username);
    }

    async addDevice(username, device_type, device_name, api_key) {
        return await this.loginModel.addDevice(username, device_type, device_name, api_key);
    }

    async deleteDevice(username, device_name) {
        return await this.loginModel.deleteDevice(username, device_name);
    }

    editDevice(username, old_device_name, new_device_name, device_type, api_key) {
        return this.loginModel.editDevice(username, old_device_name, new_device_name, device_type, api_key);
    }
}

export { LoginController };