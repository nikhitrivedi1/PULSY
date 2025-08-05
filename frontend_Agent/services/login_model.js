import fs from 'fs';
import {dirname, join} from 'path';
import { fileURLToPath } from 'url';

class LoginModel {
    constructor() {
        this.db_path = join(dirname(fileURLToPath(import.meta.url)), "../../shared/user_state.json");
        this.data = JSON.parse(fs.readFileSync(this.db_path, 'utf8'));
    }

    authenticate(username, password) {
        // Open File From Local JSON File - Placeholder for now
        return this.data[username]["password"] === password;
    }

    addUser(username, password, profile, preferences) {
        // Open File From Local JSON File - Placeholder for now
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

    checkDuplicate(username) {
        return this.data[username] !== undefined;
    }

    getUserDevices(username) {
        return this.data[username]["devices"];
    }

    async loadUserDevices(device_object) {
        // send post request to the backend API - app is run at app, host="0.0.0.0", port=8000)
        let response = await fetch(`http://0.0.0.0:8000/load_user_devices/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({device_type: device_object["device_type"], device_name: device_object["device_name"], api_key: device_object["api_key"]})
        });

        let data = await response.json();
        return data;
    }

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

    getUserProfile(username) {
        return this.data[username]["profile"];
    }

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

    async addDevice(username, device_type, device_name, api_key) {
        // User is Authenticated via session

        // Add device to the user's devices list
        // Create device object
        let device = {
            "device_type": device_type,
            "device_name": device_name,
            "api_key": api_key
        }

        // Add device to the user's devices list
        this.data[username]["devices"].push(device);

        // Write to the database
        try {
            fs.writeFileSync(this.db_path, JSON.stringify(this.data, null, 2), 'utf8');
            return true;
        } catch (error) {
            console.error('Error writing to file:', error);
            return false;
        }
    }

    async deleteDevice(username, device_name) {
        // User is Authenticated via session

        // Delete device from the user's devices list
        this.data[username]["devices"] = this.data[username]["devices"].filter(device => device["device_name"] !== device_name);

        try {
            fs.writeFileSync(this.db_path, JSON.stringify(this.data, null, 2), 'utf8');
            return true;
        } catch (error) {
            console.error('Error writing to file:', error);
            return false;
        }
    }


    editDevice(username, old_device_name, new_device_name, device_type, api_key) {
        // User is Authenticated via session

        this.data[username]["devices"] = this.data[username]["devices"].map(device => device["device_name"] === old_device_name ? { ...device, device_name: new_device_name, device_type: device_type, api_key: api_key } : device);

        try {
            fs.writeFileSync(this.db_path, JSON.stringify(this.data, null, 2), 'utf8');
            return true;
        } catch (error) {
            console.error('Error writing to file:', error);
            return false;
        }
    }

    async chatQuery(query, username, user_history, ai_chat_history) {
        // User is AUntheticated via Session
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

export { LoginModel };