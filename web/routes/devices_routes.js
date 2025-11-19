import express from 'express';

/**
 * Exports router configuration for device management routes
 * @param {Object} controller - Controller handling device management logic
 * @returns {Object} Express router instance with configured routes
 */
export default (controller) => {
    const router = express.Router();

    router.get('/authorize_oura_ring', async (req, res) => {
        console.log("req.session: ", req.session)
        // This is the redirect route for the Oura Ring authorization
        console.log("Authorizing Oura Ring");
        const code = req.query.code;
        // Get the tokens from the acces code
        let tokens = await controller.getTokensOuraRing(code);

        // Get the sesssion from the database
        let session = await controller.getSession(req.query.state);
        if (session.success) {
            req.session.username = session.return_value.username.username;
            req.session.visited = session.return_value.username.visited;
            req.session.user_devices = session.return_value.username.user_devices;
            req.session.user_metrics = session.return_value.username.user_metrics;
            req.session.response_history = session.return_value.username.response_history;
            req.session.query_history = session.return_value.username.query_history;
            req.session.device_error_message = session.return_value.username.device_error_message;
        } else {
            return res.redirect('/');
        }

        // Delete the session from the database
        const status_delete_session = await controller.deleteSession(req.query.state);
        if (status_delete_session.success) {
            console.log("Session deleted successfully");
        } else {
            console.log("Session deletion failed: ", status_delete_session.return_value);
        }

        // Update the tokens in the database
        const status = await controller.updateTokensOuraRing(req.session.username, tokens);
        console.log("Status: ", status);

        return res.redirect('/nav_bar/my_devices');
    });
    /**
     * POST /devices/action
     * Handles device addition and deletion actions
     * @param {Object} req - Express request object containing action type and device details
     * @param {Object} res - Express response object
     * @returns {Object} Rendered page with updated device list and status message
     */
    router.post('/action', async (req, res) => {
        // Handle device addition
        let status = null;
        if(req.body.action == "add") {
            console.log("Adding device");
            const device_type = req.body.device_type;
            const api_key = req.body.api_key;
            // status = await controller.addDevice(req.session.username, device_type, api_key);
            if (device_type == "Oura Ring"){
                let auth_url = await controller.authorizeOuraRingUser(req.session);
                return res.redirect(auth_url);
            }            
        } 
        // Handle device deletion
        else if(req.body.action == "delete") {
            console.log("Deleting device");
            const device_type = req.body.device_type;
            status = await controller.deleteDevice(req.session.username, device_type);
            console.log(status);
        }


        // consolidate actions after action - delete/add after complete
        if (status.success) {
            // reload the user deviceslist 
            let status_user_devices = await controller.getUserDevices(req.session.username);
            if (status_user_devices.success) {
                let user_devices_array = status_user_devices.return_value.devices;
                console.log("user_devices_array", user_devices_array)
                res.render("my_devices_page.ejs", { user_devices: user_devices_array, successMessage: "Device Reloaded successfully", errorMessage: null });
            } else {
                res.render("my_devices_page.ejs", { successMessage: null, errorMessage: status_user_devices.return_value });
            }
        } else {
            res.render("my_devices_page.ejs", { successMessage: null, errorMessage: status.return_value });
        } 
    });

    /**
     * POST /devices/edit
     * Handles editing of existing device details
     * @param {Object} req - Express request object containing updated device information
     * @param {Object} res - Express response object
     * @returns {Object} Rendered page with updated device list and status message
     */
    router.post('/edit', (req, res) => {
        const old_device_name = req.body.old_device_name;
        const new_device_name = req.body.new_device_name;
        const device_type = req.body.device_type;
        const api_key = req.body.api_key;
        const status = controller.editDevice(req.session.username, old_device_name, new_device_name, device_type, api_key);

        if (status) {
            // Reload user's devices list after successful edit
            let user_devices = controller.getUserDevices(req.session.username);
            res.render("my_devices_page.ejs", { user_devices: user_devices, successMessage: "Device edited successfully", errorMessage: null });
        } else {
            res.render("my_devices_page.ejs", { successMessage: null, errorMessage: "Device editing failed" });
        }
    });

    return router;
}