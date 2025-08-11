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
        req.session.destroy();
        res.redirect('/');
    });
    
    /**
     * GET /my_devices
     * Renders the devices page showing user's connected devices
     * @param {Object} req - Express request object containing session data
     * @param {Object} res - Express response object
     */
    router.get('/my_devices', (req, res) => {
        // Check if user has an active session
        if (req.session.visited) {
            // Fetch user's devices list from database via controller
            let user_devices = controller.getUserDevices(req.session.username);
            res.render("my_devices_page.ejs", { user_devices: user_devices});
        } else {
            // Redirect to home if no active session
            res.redirect('/');
        }
    });

    return router;
}