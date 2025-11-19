// Import Express framework
import express from 'express';

/**
 * Exports router configuration for navigation bar routes
 * @param {Object} controller - Controller handling login/authentication logic
 * @returns {Object} Express router instance with configured routes
 */
export default (controller) => {
    const router = express.Router();

    /**
     * GET /logout
     * Handles user logout by destroying session and redirecting to home
     * @param {Object} req - Express request object containing session
     * @param {Object} res - Express response object
     */
    router.get('/logout', (req, res) => {
        console.log("Logging out");
        req.session = null;
        res.redirect('/');
    });
    
    /**
     * GET /my_devices
     * Renders the devices page showing user's connected devices
     * @param {Object} req - Express request object containing session data
     * @param {Object} res - Express response object
     */
    router.get('/my_devices', async (req, res) => {
        console.log("Request Session MY DEVICES: ", req.session)
        // Check if user has an active session
        if (req.session.visited) {
            let status_user_devices = await controller.getUserDevices(req.session.username);
            if (status_user_devices.success) {
                let user_devices_array = status_user_devices.return_value.devices;
                console.log("user_devices_array", user_devices_array)
                res.render("my_devices_page.ejs", { user_devices: user_devices_array, successMessage: "Device Reloaded successfully", errorMessage: null });
            } else {
                res.render("my_devices_page.ejs", { successMessage: null, errorMessage: status_user_devices.return_value });
            }
        } else {
            // Redirect to home if no active session
            res.redirect('/');
        }
    });

    return router;
}