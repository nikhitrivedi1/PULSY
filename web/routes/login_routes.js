// Import Express framework
import express from 'express';

/**
 * Exports router configuration for login-related routes
 * @param {Object} controller - Controller handling login/authentication logic
 * @returns {Object} Express router instance with configured routes
 */
export default (controller) => {
    const router = express.Router();

    /**
     * GET /signup
     * Renders the signup page for new user registration
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     */
    router.get('/signup', (req, res) => {
        res.render("signup_page.ejs");
    });
    
    /**
     * POST /signup
     * Handles new user registration form submission
     * @param {Object} req - Express request object containing form data
     * @param {Object} res - Express response object
     */
    router.post('/signup', async (req, res) => {
        // Extract user credentials from request body
        var username = req.body.newUsername;
        var password = req.body.newPassword;
    
        // Build user profile object from form data
        var profile = {
            age : req.body.age,
            gender : req.body.gender,
            height_ft : req.body.height_ft,
            height_in : req.body.height_in,
            weight : req.body.weight,
            health_conditions : req.body.health_conditions
        }
        // Get user preferences from form
        var preferences = req.body.preferences;
    
        // Attempt to create new user account
        var status = await controller.addUser(username, password, profile, preferences);
        if (status) {
            // Render signup page with success message if user created
            res.render("signup_page.ejs", { successMessage: "User created successfully", errorMessage: null });
        } else {
            // Render signup page with error if creation failed
            res.render("signup_page.ejs", { successMessage: null, errorMessage: "User creation failed" });
        }
    });

    return router;
}