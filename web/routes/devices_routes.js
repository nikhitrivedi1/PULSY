import express from 'express';

/**
 * Exports router configuration for device management routes
 * @param {Object} controller - Controller handling device management logic
 * @returns {Object} Express router instance with configured routes
 */
export default (controller) => {
    const router = express.Router();

    /**
     * POST /devices/action
     * Handles device addition and deletion actions
     * @param {Object} req - Express request object containing action type and device details
     * @param {Object} res - Express response object
     * @returns {Object} Rendered page with updated device list and status message
     */
    router.post('/action', async (req, res) => {
        // Handle device addition
        if(req.body.action == "add") {
            const device_type = req.body.device_type;
            const device_name = req.body.device_name;
            const api_key = req.body.api_key;

            const status = await controller.addDevice(req.session.username, device_type, device_name, api_key);
            if (status) {
                // Reload the user's devices list after successful addition
                let user_devices = await controller.getUserDevices(req.session.username);
                res.render("my_devices_page.ejs", { user_devices: user_devices, successMessage: "Device added successfully", errorMessage: null });
            } else {
                res.render("my_devices_page.ejs", { successMessage: null, errorMessage: "Device addition failed" });
            }
        } 
        // Handle device deletion
        else if(req.body.action == "delete") {
            const device_name = req.body.device_name;
            const status = await controller.deleteDevice(req.session.username, device_name);
            console.log(status);
            if (status) {
                // Reload the user's devices list after successful deletion
                let user_devices = await controller.getUserDevices(req.session.username);
                res.render("my_devices_page.ejs", { user_devices: user_devices, successMessage: "Device deleted successfully", errorMessage: null });
            }
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