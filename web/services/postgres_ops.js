import argon2 from 'argon2';
import Knex from 'knex';
import {Connector} from '@google-cloud/cloud-sql-connector';

class UserDbOperations {
  constructor() {
    if (process.env.LOCAL_MODE === 'true') {
      console.log("Local mode enabled");
      this.pool = Promise.resolve(Knex({
        client: 'pg',
        connection: {
          host: process.env.PUBLIC_IP,
          port: process.env.DB_PORT,
          user: process.env.DB_USERNAME,
          password: process.env.PASSWORD,
          dbname: process.env.DATABASE_NAME,
          ssl:{
            rejectUnauthorized: false,
          }
        }
      }));
    }else{
      const connector = new Connector();
      this.pool = (async () => {
        const clientOpts = await connector.getOptions({
          instanceConnectionName: process.env.INSTANCE_CONNECTION_NAME,
          ipType: process.env.IP_TYPE,
        });
    
        return Knex({
          client: 'pg',
          connection: {
            ...clientOpts,
            user: process.env.USERNAME,
            password: process.env.PASSWORD,
            database: process.env.DATABASE_NAME,
          }
        });
      })();
    }
  }
  

  async hashPassword(password) {
    return await argon2.hash(password);
  }

  async verifyPassword(provided_password, username) {
    const query = `
      SELECT password, id FROM users.users_staging WHERE username = ?`;
    const knex_res = await this.pool
    const res = await knex_res.raw(query, [username]);
    console.log("res: ", res.rows)
    if (res.rows.length === 0) return null;
    return await argon2.verify(res.rows[0].password, provided_password);
  }

  // Upload User Data
  async uploadUserData(userData) {
    const {username, password, preferences, devices, first_name, last_name } = userData;
    // Check to see if username already exists
    const check_query = `
      SELECT id FROM users.users_staging WHERE username = ?
    `;
    const knex_res = await this.pool
    const check_res = await knex_res.raw(check_query, [username]);
    if (check_res.rows.length > 0) return { success: false, error: "Username already exists" };

    const query = `
      INSERT INTO users.users_staging (username, password, preferences, devices, first_name, last_name)
      VALUES (?, ?, ?, ?, ?, ?) RETURNING id, username
    `;
    const values = [
      username,
      await this.hashPassword(password),
      [preferences],  // Expecting an array of strings
      devices,      // Expecting an object, will be stored as JSONB
      first_name,
      last_name
    ];
    try {
      const knex_res = await this.pool;
      const res = await knex_res.raw(query, values);
      return { success: true, id: res.rows[0].id, username: res.rows[0].username };
    } catch (error) {
      console.error('Error uploading user data:', error);
      return { success: false, error: error.message };
    }
  }

  // Get Device Information
  async getDeviceInformation(username) {
    // Assuming devices are in users table as a JSONB column on users_staging
    // You might want to adapt this based on your schema
    const query = `
      SELECT devices FROM users.users_staging WHERE username = ?
    `;
    try{
      const knex_res = await this.pool;
      const res = await knex_res.raw(query, [username]);
      if (res.rows.length === 0) return { success: false, return_value: "No devices found" };
      return { success: true, return_value: res.rows[0]};
    } catch (error) {
      console.error('Error getting device information:', error);
      return { success: false, return_value: error.detail };
    }
  }

  async storeState(state, username) {
    const query = `
    INSERT INTO users.state_to_username (state, username) VALUES (?, ?)
    `;
    try{
      const knex_res = await this.pool;
      await knex_res.raw(query, [state, username]);
      return { success: true, return_value: "State stored successfully" };
    } catch (error) {
      console.error('Error storing state:', error);
      return { success: false, return_value: error.detail };
    }
  }

  async getSession(state) {
    const query = `
    SELECT username FROM users.state_to_username WHERE state = ?
    `;
    try{
      const knex_res = await this.pool;
      const res = await knex_res.raw(query, [state]);
      return { success: true, return_value: res.rows[0] };
    } catch (error) {
      console.error('Error getting session:', error);
      return { success: false, return_value: error.detail };
    }
  }

  async deleteSession(state) {
    const query = `
    DELETE FROM users.state_to_username WHERE state = ?
    `;
    try{
      const knex_res = await this.pool;
      await knex_res.raw(query, [state]);
      return { success: true, return_value: "Session deleted successfully" };
    } catch (error) {
      console.error('Error deleting session:', error);
      return { success: false, return_value: error.detail };
    }
  }


  // Get Agentic Preferences
  async getAgenticPreferences(username) {
    const query = `
      SELECT preferences FROM users.users_staging WHERE username = ?
    `;
    console.log("Username: ", username);
    try{
      const knex_res = await this.pool;
      const res = await knex_res.raw(query, [username]);
      if (res.rows.length === 0) return null;
      return res.rows[0].preferences;
    } catch (error) {
      console.error('Error getting agentic preferences:', error);
      return { success: false, return_value: error.detail };
    }
  }

  // Add Agentic Preference
  async addAgenticPreference(username, preference) {
    // Array append in PG: array_append
    const query = `
      UPDATE users.users_staging
      SET preferences = preferences || ARRAY[?]
      WHERE username = ? RETURNING preferences
    `;
    try{
      const knex_res = await this.pool;
      const res = await knex_res.raw(query, [preference, username]);
      return { success: true, return_value: res.rows[0].preferences };
    } catch (error) {
      console.error('Error adding agentic preference:', error);
      return { success: false, return_value: error.detail };
    }
  }

  // Remove Agentic Preference
  async removeAgenticPreference(username, preference) {
    // array_remove in PG
    const query = `
      UPDATE users.users_staging
      SET preferences = array_remove(preferences, ?)
      WHERE username = ? RETURNING preferences
    `;
    try{
      const knex_res = await this.pool;
      const res = await knex_res.raw(query, [preference, username]);
      return { success: true, return_value: res.rows[0].preferences };
    } catch (error) {
      console.error('Error removing agentic preference:', error);
      return { success: false, return_value: error.detail };
    }
  }

  // Add Device
  async addDevice(username, device) {
    const query = `
    UPDATE users.users_staging
    SET devices = devices || jsonb_build_object(?, ?)
    WHERE username = ?
  `;
  console.log("query: ", device);
    try{
      const knex_res = await this.pool;
      await knex_res.raw(query, [device.device_type, device.api_key, username]);
      console.log("Device added successfully");
      return { success: true, return_value: "Device added successfully" };
    } catch (error) {
      console.error('Error adding device:', error);
      return { success: false, return_value: error.detail };
    }
  }

  // Update Tokens
  async updateTokensOuraRing(username, tokens) {
    const query = `
      UPDATE users.users_staging
      SET devices = jsonb_set(devices, '{Oura Ring}', ?)
      WHERE username = ?
    `;
    try{
      const knex_res = await this.pool;
      await knex_res.raw(query, [JSON.stringify(tokens), username]);
      return { success: true, return_value: "Tokens updated successfully" };
    } catch (error) {
      console.error('Error updating tokens:', error);
      return { success: false, return_value: error.detail };
    }
  }

  async refreshTokens(username) {
    // get the refresh_token from the database
    const query = `
      SELECT devices->'Oura Ring'->>'refresh_token' FROM users.users_staging WHERE username = ?
    `;
    const knex_res = await this.pool;
    const res = await knex_res.raw(query, [username]);
    if (res.rows.length === 0) return { success: false, return_value: "No refresh token found" };
    const refresh_token = res.rows[0].refresh_token;
    return { success: true, return_value: refresh_token };
  }

  // Delete Device
  async deleteDevice(username, device_type) {
    const query = `
      UPDATE users.users_staging
      SET devices = devices - ?
      WHERE username = ?
    `;
    try{
      const knex_res = await this.pool;
      await knex_res.raw(query, [device_type, username]);
      return { success: true, return_value: "Device deleted successfully" };
    } catch (error) {
      console.error('Error deleting device:', error);
      return { success: false, return_value: error.detail };
    }
  }

  // Add Feedback
  async addFeedback(log_id, feedback, preferred_response) {
    // create json object for feedback and comment
    const query = `
      UPDATE logging.logger_final
      SET feedback = ?, preferred_response = ?
      WHERE id = ?
    `;
    try{
      console.log("Adding feedback: ", feedback, preferred_response, log_id);
      const knex_res = await this.pool;
      await knex_res.raw(query, [feedback ?? null, preferred_response ?? null, log_id]);
      return { success: true, return_value: "Feedback added successfully" };
    } catch (error) {
      console.error('Error adding feedback:', error);
      return { success: false, return_value: error.detail };
    }
  }

  // Close connection pool
  async closeConnection() {
    const knex = await this.pool;
    await knex.destroy();
  }
}

export default UserDbOperations;