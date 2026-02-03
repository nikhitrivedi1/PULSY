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
                // Load chat history from database instead of session
                let query_history = [];
                let response_history = [];
                
                try {
                    const historyResult = await controller.getChatHistory(req.session.username);
                    if (historyResult.success && historyResult.return_value) {
                        query_history = historyResult.return_value.queries || [];
                        response_history = historyResult.return_value.responses || [];
                        // Update session log_id if available
                        if (historyResult.return_value.log_id) {
                            req.session.log_id = historyResult.return_value.log_id;
                        }
                    }
                } catch (historyError) {
                    console.error("Error loading chat history from DB:", historyError);
                    // Fall back to session if DB fails
                    query_history = req.session.query_history || [];
                    response_history = req.session.response_history || [];
                }
        
                // Render the chat page
                res.status(200).render("chat_page", { 
                    user_metrics: req.session.user_metrics, 
                    user_devices: req.session.user_devices, 
                    errorMessage: req.session.device_error_message, 
                    query_history: query_history, 
                    response_history: response_history 
                });
            }
        } else {
            res.status(200).render("loginPage.ejs", { errorMessage: "Invalid username or password" });
        }
    });

    /**
     * POST /chat/refresh_tokens
     * Refreshes OAuth tokens for a disconnected device
     * Uses the OAuth2 refresh token flow to obtain new access tokens
     * @param {Object} req - Express request object containing device_type in body
     * @param {Object} res - Express response object
     */
    router.post('/refresh_tokens', async (req, res) => {
        const device_type = req.body.device_type;
        let errorMessage = null;
        let successMessage = null;

        try {
            // Currently only supporting Oura Ring
            if (device_type === "Oura Ring") {
                console.log("Refreshing Oura Ring tokens for user:", req.session.username);
                
                // Step 1: Refresh the tokens using OAuth2 refresh token flow
                let refresh_result = await controller.refreshOuraTokens(req.session.username);
                
                if (refresh_result.success) {
                    console.log("Token refresh successful, testing new connection...");
                    
                    // Step 2: Test the new access token
                    const new_tokens = refresh_result.return_value;
                    let is_connected = await controller.testUserDevices("Oura Ring", new_tokens.access_token);
                    
                    if (is_connected) {
                        // Step 3: Update session with new device status
                        let devices_response = await controller.getUserDevices(req.session.username);
                        if (devices_response.success) {
                            // Rebuild devices array with updated status
                            let devices_array = [];
                            for (const [key, tokens] of Object.entries(devices_response.return_value.devices)) {
                                let device_connected = await controller.testUserDevices(key, tokens.access_token);
                                devices_array.push({
                                    device_type: key, 
                                    device_status: device_connected ? "pass" : "fail"
                                });
                            }
                            req.session.user_devices = devices_array;
                        }
                        successMessage = "Device reconnected successfully!";
                    } else {
                        errorMessage = "Token refresh succeeded but connection test failed. Please try reconnecting your device.";
                    }
                } else {
                    console.error("Token refresh failed:", refresh_result.return_value);
                    errorMessage = `Failed to refresh tokens: ${refresh_result.return_value}`;
                }
            } else {
                errorMessage = `Token refresh not supported for ${device_type}`;
            }
        } catch (error) {
            console.error("Error in refresh_tokens route:", error);
            errorMessage = "An unexpected error occurred while refreshing tokens.";
        }

        // Render chat page preserving all session state
        res.render("chat_page.ejs", { 
            user_metrics: req.session.user_metrics || [], 
            user_devices: req.session.user_devices || [], 
            query_history: req.session.query_history || [],
            response_history: req.session.response_history || [],
            successMessage: successMessage,
            errorMessage: errorMessage
        });
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
     * POST /chat/save-history
     * Saves chat history to database after streaming completes
     * Called by frontend after SSE streaming is done
     * @param {Object} req - Express request with query, response, log_id in body
     * @param {Object} res - Express response object
     */
    router.post('/save-history', async (req, res) => {
        try {
            const { query, response, log_id } = req.body;
            const username = req.session.username;

            if (!username) {
                return res.status(401).json({ success: false, error: "Not authenticated" });
            }

            if (!query || !response) {
                return res.status(400).json({ success: false, error: "Missing query or response" });
            }

            const result = await controller.saveChatHistory(username, query, response, log_id);
            
            if (result.success) {
                // Also update session log_id for feedback
                req.session.log_id = log_id;
                res.status(200).json({ success: true });
            } else {
                console.error("Failed to save chat history:", result.return_value);
                res.status(500).json({ success: false, error: result.return_value });
            }
        } catch (error) {
            console.error("Error in /save-history route:", error);
            res.status(500).json({ success: false, error: error.message });
        }
    });

    /**
     * POST /chat/clear-history
     * Clears all chat history for the current user
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     */
    router.post('/clear-history', async (req, res) => {
        try {
            const username = req.session.username;

            if (!username) {
                return res.status(401).json({ success: false, error: "Not authenticated" });
            }

            const result = await controller.clearChatHistory(username);
            
            if (result.success) {
                res.status(200).json({ success: true });
            } else {
                console.error("Failed to clear chat history:", result.return_value);
                res.status(500).json({ success: false, error: result.return_value });
            }
        } catch (error) {
            console.error("Error in /clear-history route:", error);
            res.status(500).json({ success: false, error: error.message });
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

    /**
     * GET /chat/query/stream
     * Streams AI chat responses using Server-Sent Events (SSE)
     * Proxies the SSE stream from the Python backend to the frontend
     * 
     * Query Parameters:
     * - query: User's question/query
     * 
     * @param {Object} req - Express request object containing session and query params
     * @param {Object} res - Express response object configured for SSE
     */
    router.get('/query/stream', async (req, res) => {
        const query = req.query.query;
        const username = req.session.username;
        
        if (!query || !username) {
            res.setHeader('Content-Type', 'text/event-stream');
            res.setHeader('Cache-Control', 'no-cache');
            res.setHeader('Connection', 'keep-alive');
            res.write(`data: ${JSON.stringify({ type: 'error', message: 'Missing query or username' })}\n\n`);
            res.end();
            return;
        }

        // Load chat history from database for context (session won't persist after flushHeaders)
        let query_history = [];
        let response_history = [];
        
        try {
            const historyResult = await controller.getChatHistory(username);
            if (historyResult.success && historyResult.return_value) {
                query_history = historyResult.return_value.queries || [];
                response_history = historyResult.return_value.responses || [];
            }
        } catch (historyError) {
            console.error("Error loading chat history for streaming:", historyError);
        }
        
        // Add current query to the history for context
        query_history.push(query);

        // Set SSE headers
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
        res.setHeader('X-Accel-Buffering', 'no'); // Disable nginx buffering
        res.flushHeaders();

        try {
            // Get streaming response from model
            const streamIterator = await controller.chatQueryStream(
                query, 
                username, 
                query_history, 
                response_history
            );

            // Process and forward each event
            for await (const event of streamIterator) {
                // Forward the event to client
                res.write(`data: ${JSON.stringify(event)}\n\n`);
            }

            // Note: Session updates are NOT possible after flushHeaders() with cookie-session
            // Frontend will call /save-history to persist the response to database
            res.end();

        } catch (error) {
            console.error('Error in /query/stream route:', error);
            res.write(`data: ${JSON.stringify({ type: 'error', message: error.message })}\n\n`);
            res.end();
        }
    });

    return router;
}