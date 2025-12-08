/**
 * Main server application file for the frontend agent
 * @module server
 */

/** External Dependencies */
import express from 'express';
import cookieSession from 'cookie-session';
import { fileURLToPath } from 'url';
import path from 'path';

/** Internal Dependencies */
import { Controller } from './controllers/controller.js';
import loginRoutes from './routes/login_routes.js';
import userProfileRoutes from './routes/user_profile_routes.js';
import chatRoutes from './routes/chat_routes.js';
import devicesRoutes from './routes/devices_routes.js';
import navBarRoutes from './routes/nav_bar_routes.js';

/** Configure file paths and initialize Express app */
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const port = process.env.PORT || 3000;
const controller = new Controller(null, null);

/** Configure Express settings and middleware */
app.set('view engine', 'ejs');
app.set('trust proxy', 1); // Trust first proxy (required for Cloud Run behind load balancer)

// Configure cookie-based session middleware
app.use(
    cookieSession({
        name: 'session',
        keys: [
            process.env.SESSION_SECRET || 'dev-secret-1', // Primary key for signing
            process.env.SESSION_SECRET_2 || 'dev-secret-2', // Secondary key for key rotation
        ],
        httpOnly: true, // Prevents client-side JS from accessing cookies
        secure: process.env.LOCAL_MODE === 'true' ? false : true, // Require HTTPS in production
        sameSite: 'lax', // CSRF protection - allows navigation from external sites
        maxAge: 60 * 60 * 24 * 1000, // Session expiry: 24 hours
      })
);
app.use(express.json()); // Parse JSON request bodies
app.use(express.urlencoded({ extended: true }));

/** Serve static assets */
app.use('/assets', express.static(path.join(__dirname, 'assets')));

/** Mount route handlers */
app.use('/login', loginRoutes(controller));
app.use('/user_profile', userProfileRoutes(controller));
app.use('/chat', chatRoutes(controller));
app.use('/my_devices', devicesRoutes(controller));
app.use('/nav_bar', navBarRoutes(controller));
app.use('/chat/sources', express.static(path.join(__dirname, 'knowledge_sources')));

/** Default route handler */
app.get('/', (req, res) => {
    res.render("loginPage.ejs")
});

/** Start server */
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});