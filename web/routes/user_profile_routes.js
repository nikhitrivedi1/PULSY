/**
 * User Profile Management Routes
 * 
 * Handles user profile operations:
 * - View user profile and preferences
 * - Update profile information
 * - Add/remove user preferences
 * 
 * @module user_profile_routes
 */

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
    router.get('/home', async (req, res) => {
        try{
            let user_preferences = await controller.getUserProfile(req.session.username);
            res.render("user_profile.ejs", { user_preference: user_preferences, successMessage: null, errorMessage: null });
        } catch (error) {
            res.render("user_profile.ejs", { successMessage: null, errorMessage: error.message });
        }
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


    /**
     * POST /user_profile/add_preference
     * Adds a new preference to user's profile
     * @param {Object} req - Express request object with preference in body
     * @param {Object} res - Express response object
     */
    router.post('/add_preference', async (req, res) => {
        let user_preference = await controller.addUserPreference(req.session.username, req.body.preference);
        if (user_preference.success) {
            res.render("user_profile.ejs", { user_preference: user_preference.return_value, successMessage: "Preference added successfully", errorMessage: null });
        } else {
            res.render("user_profile.ejs", { user_preference: null, successMessage: null, errorMessage: user_preference.return_value });
        }
    });

    /**
     * POST /user_profile/delete_preference
     * Removes a preference from user's profile
     * @param {Object} req - Express request object with preference in body
     * @param {Object} res - Express response object
     */
    router.post('/delete_preference', async (req, res) => {
        let user_preference = await controller.deleteUserPreference(req.session.username, req.body.preference);
        if (user_preference.success) {
            console.log(user_preference.return_value);
            res.render("user_profile.ejs", { user_preference: user_preference.return_value, successMessage: "Preference deleted successfully", errorMessage: null });
        } else {
            res.render("user_profile.ejs", { user_preference: null, successMessage: null, errorMessage: user_preference.return_value });
        }
    });
    
    return router;
}