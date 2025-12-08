/**
 * Exports router configuration for chat routes
 * @param {Object} controller - Controller handling chat logic
 * @returns {Object} Express router instance with configured routes
 */

// TODO: Figure out how to handle goal creation by refreshing the chat page - when a goal is created via tool calling
import express from 'express'
import { marked } from 'marked';
// import DOMPurify from "dompurify";


export default (controller) => {
    const router = express.Router();

    router.post('/login', async (req, res) => {
        console.log("POST /login - req.body:", req.body);
        console.log("POST /login - username:", req.body.username);
        console.log("POST /login - password:", req.body.password ? "***" : undefined);
        
        let isAuthenticated = await controller.authenticate(req.body.username, req.body.password);
        console.log("isAuthenticated: ", isAuthenticated)
        if (isAuthenticated) {
            req.session.username = req.body.username;
            req.session.visited = true;
            console.log("req.session: ", req.session)
            res.status(200).redirect("/chat/home");
        } else {
            res.status(200).render("loginPage.ejs", { errorMessage: "Invalid username or password" });
        }
    });

    /**
     * GET /chat/home
     * Renders the chat page with user metrics and goals
     * @param {Object} req - Express request object containing session data
     * @param {Object} res - Express response object
     */
    router.get('/home', async (req, res) => {
        
        if (req.session.visited) {
            // Load the user's metrics from the database
            try{
                let user_metrics = await controller.loadUserMetrics(req.session.username);
                let response = await controller.getUserDevices(req.session.username);
                let devices_array = [];

                if (response.success){
                    for (const [key, tokens] of Object.entries(response.return_value.devices)) {
                        let is_connected = await controller.testUserDevices(key, tokens.access_token);
                        if (is_connected) {
                            devices_array.push({device_type: key, device_status: "pass"});
                        } else {
                            devices_array.push({device_type: key, device_status: "fail"});
                        }
                    }
                }
                // Verify the devices are connected
                req.session.user_metrics = user_metrics;
                req.session.user_devices = devices_array;
            } catch (error) {
                console.log(error)
                let user_metrics = {};
                req.session.user_metrics = user_metrics;
                req.session.device_error_message = error.message;
                req.session.user_devices = [];
            }finally{
        
                if (!req.session.query_history){
                    req.session.query_history = [];
                }
                if (!req.session.response_history){
                    req.session.response_history = [];
                }
        
                // Render the chat page
                res.status(200).render("chat_page", { user_metrics: req.session.user_metrics, user_devices: req.session.user_devices, errorMessage: req.session.device_error_message, query_history: req.session.query_history, response_history: req.session.response_history });
            }
        } else {
            res.status(200).render("loginPage.ejs", { errorMessage: "Invalid username or password" });
        }
    });

    router.get('/refresh_tokens', async (req, res) => {
        // TODO: Add other devices types at a later time
        if (req.device_type == "Oura Ring") {
            let response = await controller.refreshTokens(req.session.username);
            // Update the user devices status
            if (response.success) {
                let user_devices = await controller.getUserDevices(req.session.username);
                if (user_devices.success) {
                    req.session.user_devices = user_devices.return_value.devices;
                }
            }
        } 
        res.render("chat_page.ejs", { user_metrics: req.session.user_metrics, user_devices: req.session.user_devices, successMessage: "Tokens refreshed successfully", errorMessage: null });
    });

    router.post('/feedback', async (req, res) => {
        const feedback = req.body.feedback;
        const comment = req.body.comment;
        console.log("Feedback received: ", feedback, comment, req.session.log_id);
        const status = await controller.addFeedback(req.session.log_id, feedback, comment);
        if (status.success) {
            res.status(200).json({ success: true, message: "Feedback submitted successfully" });
        } else {
            console.error("Failed to submit feedback:", status.error);
            res.status(500).json({ success: false, message: status.error });
        }
    });

    /**
     * POST /chat/query
     * Handles chat queries asynchronously and returns JSON response
     * @param {Object} req - Express request object containing query data
     * @param {Object} res - Express response object
     */
    router.post('/query', async (req, res) => {
        try {
            const query = req.body.query;
            const username = req.session.username;
            
            if (!query || !username) {
                return res.status(400).json({ 
                    success: false, 
                    error: "Missing query or username" 
                });
            }
            
            // Add query to history
            if (!req.session.query_history) {
                req.session.query_history = [];
            }
            if (!req.session.response_history) {
                req.session.response_history = [];
            }
            req.session.query_history.push(query);
        
            // Get AI response
            const response_data = await controller.chatQuery(
                query, 
                username, 
                req.session.query_history, 
                req.session.response_history
            );
            
            const response = response_data.response;
            const log_id = response_data.log_id;
            const marked_response = marked(response);
            console.log(marked_response);
            console.log("Query processed successfully, Log ID:", log_id);
            
            req.session.response_history.push(marked_response);
            req.session.log_id = log_id;

            res.status(200).json({ 
                success: true,
                response: marked_response,
                log_id: log_id 
            });
        } catch (error) {
            console.error("Error in /query route:", error);
            res.status(500).json({ 
                success: false, 
                error: "Failed to process query",
                message: error.message 
            });
        }
    });
    return router;
}