import express from 'express';

/**
 * Exports router configuration for user profile routes
 * @param {Object} controller - Controller handling user profile logic
 * @returns {Object} Express router instance with configured routes
 */
export default (controller) => {
    const router = express.Router();

    /**
     * GET /user_profile/home
     * Renders the user profile page with the user's current profile information
     * @param {Object} req - Express request object containing session data
     * @param {Object} res - Express response object
     */
    router.get('/home', (req, res) => {
        const user_profile = controller.getUserProfile(req.session.username);
        res.render("user_profile.ejs", { user_profile: user_profile, successMessage: null, errorMessage: null });
    });
    
    /**
     * POST /user_profile/update
     * Updates the user's profile with submitted form data
     * @param {Object} req - Express request object containing form data in body
     * @param {Object} res - Express response object
     */
    router.post('/update', (req, res) => {
        const user_profile = controller.updateUserProfile(req.session.username, req.body);
        res.render("user_profile.ejs", { user_profile: user_profile, successMessage: "Profile updated successfully", errorMessage: null });
    });
    
    return router;
}