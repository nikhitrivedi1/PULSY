import argon2 from 'argon2';
import Knex from 'knex';
import {Connector} from '@google-cloud/cloud-sql-connector';

class UserDbOperations {
  constructor() {
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
  
    this.connector = connector;
  }
  

  async hashPassword(password) {
    return await argon2.hash(password);
  }

  async verifyPassword(provided_password, username) {
    const query = `
      SELECT password, id FROM users.users_staging WHERE username = $1
    `;
    const res = await this.pool.raw(query, [username]);
    if (res.rows.length === 0) return null;
    return await argon2.verify(res.rows[0].password, provided_password) ? res.rows[0].id : null;
  }

  // Upload User Data
  async uploadUserData(userData) {
    const {username, password, preferences, devices, first_name, last_name } = userData;
    // Check to see if username already exists
    const check_query = `
      SELECT id FROM users.users_staging WHERE username = $1
    `;
    const check_res = await this.pool.raw(check_query, [username]);
    if (check_res.rows.length > 0) return { success: false, error: "Username already exists" };


    const query = `
      INSERT INTO users.users_staging (username, password, preferences, devices, first_name, last_name)
      VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, username
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
      let res = await this.pool.raw(query, values);
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
      SELECT devices FROM users.users_staging WHERE username = $1
    `;
    try{
      let res = await this.pool.raw(query, [username]);
      console.log(res.rows);
      if (res.rows.length === 0) return { success: false, return_value: "No devices found" };
      return { success: true, return_value: res.rows[0]};
    } catch (error) {
      console.error('Error getting device information:', error);
      return { success: false, return_value: error.detail };
    }
  }


  // Get Agentic Preferences
  async getAgenticPreferences(username) {
    const query = `
      SELECT preferences FROM users.users_staging WHERE username = $1
    `;
    try{
    let res = await this.pool.raw(query, [username]);
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
      SET preferences = preferences || ARRAY[$1]
      WHERE username = $2 RETURNING preferences
    `;
    try{
      let res = await this.pool.raw(query, [preference, username]);
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
      SET preferences = array_remove(preferences, $1)
      WHERE username = $2 RETURNING preferences
    `;
    try{
      let res = await this.pool.raw(query, [preference, username]);
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
    SET devices = devices || jsonb_build_object($1::text, $2::text)
    WHERE username = $3
  `;
  
    try{
      await this.pool.query(query, [device.device_type, device.api_key, username]);
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
      SET devices = jsonb_set(devices, '{Oura Ring}', $1::jsonb)
      WHERE username = $2
    `;
    console.log("Tokens: ", JSON.stringify(tokens));
    try{
      await this.pool.query(query, [JSON.stringify(tokens), username]);
      return { success: true, return_value: "Tokens updated successfully" };
    } catch (error) {
      console.error('Error updating tokens:', error);
      return { success: false, return_value: error.detail };
    }
  }

  async refreshTokens(username) {
    // get the refresh_token from the database
    const query = `
      SELECT devices->'Oura Ring'->>'refresh_token' FROM users.users_staging WHERE username = $1
    `;
    const res = await this.pool.raw(query, [username]);
    if (res.rows.length === 0) return { success: false, return_value: "No refresh token found" };
    const refresh_token = res.rows[0].refresh_token;
    return { success: true, return_value: refresh_token };
  }

  // Delete Device
  async deleteDevice(username, device_type) {
    const query = `
      UPDATE users.users_staging
      SET devices = devices - $1::text
      WHERE username = $2
    `;
    try{
      await this.pool.raw(query, [device_type, username]);
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
      SET feedback = $1, preferred_response = $2
      WHERE id = $3
    `;
    try{
      await this.pool.raw(query, [feedback, preferred_response, log_id]);
      return { success: true, return_value: "Feedback added successfully" };
    } catch (error) {
      console.error('Error adding feedback:', error);
      return { success: false, return_value: error.detail };
    }
  }

  // Close connection pool
  async closeConnection() {
    await this.pool.end();
  }
}

export default UserDbOperations;