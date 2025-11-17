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
const port = 3000;
const controller = new Controller(null, null);

/** Configure Express settings and middleware */
app.set('view engine', 'ejs');
app.use(express.json()); // Parse JSON request bodies
app.use(express.urlencoded({ extended: true }));
app.use(
    cookieSession({
        name: 'session',
        keys: [process.env.SESSION_SECRET],
        httpOnly: true,
        secure: true,      // Cloud Run requires HTTPS → always true in production
        sameSite: 'lax',   // CSRF protection
        maxAge: undefined, // Session cookie → deleted when browser closes
      })
);

/** Serve static assets */
app.use('/assets', express.static(path.join(__dirname, 'assets')));

/** Mount route handlers */
app.use('/login', loginRoutes(controller));
app.use('/user_profile', userProfileRoutes(controller));
app.use('/chat', chatRoutes(controller));
app.use('/my_devices', devicesRoutes(controller));
app.use('/nav_bar', navBarRoutes(controller));

/** Default route handler */
app.get('/', (req, res) => {
    res.render("loginPage.ejs")
});

/** Start server */
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});