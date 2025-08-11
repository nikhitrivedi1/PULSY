/**
 * Exports router configuration for chat routes
 * @param {Object} controller - Controller handling chat logic
 * @returns {Object} Express router instance with configured routes
 */

// TODO: Figure out how to handle goal creation by refreshing the chat page - when a goal is created via tool calling

import express from 'express'
import { marked } from 'marked';

export default (controller) => {
    const router = express.Router();

    /**
     * GET /chat/home
     * Renders the chat page with user metrics and goals
     * @param {Object} req - Express request object containing session data
     * @param {Object} res - Express response object
     */
    router.get('/home', async (req, res) => {
        // Check if session is already authenticated
        if (req.session.visited) {
            console.log("Session already authenticated");
            res.render("chat_page.ejs", { user_metrics: req.session.user_metrics, user_goals: req.session.user_goals, response_history: req.session.response_history, query_history: req.session.query_history });
            return;
        }
    
        // Authenticate the user
        let isAuthenticated = controller.authenticate(req.query.username, req.query.password);
        if (isAuthenticated) {
            // Modify the session object to include the username
            req.session.username = req.query.username;
            req.session.visited = true;
    
            // Load the user's metrics from the database
            const user_metrics = await controller.loadUserMetrics(req.session.username);
            req.session.user_metrics = user_metrics;
    
            // Load the user's goals from the database
            const user_goals = await controller.loadUserGoals(req.session.username);
            req.session.user_goals = user_goals;
    
            req.session.query_history = [];
            req.session.response_history = [];
    
            // Render the chat page
            res.render("chat_page.ejs", { user_metrics: user_metrics, user_goals: user_goals });
        } else {
            res.render("loginPage.ejs", { errorMessage: "Invalid username or password" });
        }
    });

    /**
     * POST /chat/query
     * Handles chat queries and updates the chat page
     * @param {Object} req - Express request object containing query data
     * @param {Object} res - Express response object
     */
    router.post('/query', async (req, res) => {
        const query = req.body.query;
        const username = req.session.username;
        // Render chat page with query while response will process in the background
        req.session.query_history.push(query);
    
        const response = await controller.chatQuery(query, username, req.session.query_history, req.session.response_history);
        const marked_response = marked(response);
        req.session.response_history.push(marked_response);
    
        res.render("chat_page.ejs", { user_metrics: req.session.user_metrics, query_history: req.session.query_history, response_history: req.session.response_history, marked_response: marked_response, user_goals: req.session.user_goals });
    });

    return router;
}