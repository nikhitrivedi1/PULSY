/**
 * Main server application file for the frontend agent
 * @module server
 */

/** External Dependencies */
import express from 'express';
import session from 'express-session';
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
app.use(express.urlencoded({ extended: true }));
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        maxAge: 60 * 60 * 1000, // 1 hour
    }
}));

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

/** Legacy route handlers - commented out but preserved for reference */
/**
 * Routes for Login Page
 */
// app.get('/chat', async (req, res) => {

//     // Check if session is already authenticated
//     if (req.session.visited) {
//         console.log("Session already authenticated");
//         res.render("chat_page.ejs", { user_metrics: req.session.user_metrics, user_goals: req.session.user_goals });
//         return;
//     }

//     // Authenticate the user
//     let isAuthenticated = loginController.authenticate(req.query.username, req.query.password);
//     if (isAuthenticated) {
//         // Modify the session object to include the username
//         req.session.username = req.query.username;
//         req.session.visited = true;

//         // Load the user's metrics from the database
//         const user_metrics = await loginController.loadUserMetrics(req.session.username);
//         req.session.user_metrics = user_metrics;

//         // Load the user's goals from the database
//         const user_goals = await loginController.loadUserGoals(req.session.username);
//         req.session.user_goals = user_goals;

//         req.session.query_history = [];
//         req.session.response_history = [];

//         // Render the chat page
//         res.render("chat_page.ejs", { user_metrics: user_metrics, user_goals: user_goals });
//     } else {
//         res.render("loginPage.ejs", { errorMessage: "Invalid username or password" });
//     }
// });

// app.get('/signup', (req, res) => {
//     res.render("signup_page.ejs");
// });

// app.post('/signup', async (req, res) => {
//     var username = req.body.newUsername;
//     var password = req.body.newPassword;

//     var profile = {
//         age : req.body.age,
//         gender : req.body.gender,
//         height_ft : req.body.height_ft,
//         height_in : req.body.height_in,
//         weight : req.body.weight,
//         health_conditions : req.body.health_conditions
//     }
//     var preferences = req.body.preferences;

//     var status = await loginController.addUser(username, password, profile, preferences);
//     if (status) {
//         res.render("signup_page.ejs", { successMessage: "User created successfully", errorMessage: null });
//     } else {
//         res.render("signup_page.ejs", { successMessage: null, errorMessage: "User creation failed" });
//     }
// });

/**
 * Routes for User Profile Page
 */
// app.get('/user_profile', (req, res) => {
//     const user_profile = loginController.getUserProfile(req.session.username);
//     res.render("user_profile.ejs", { user_profile: user_profile, successMessage: null, errorMessage: null });
// });

// app.post('/update_profile', (req, res) => {
//     const user_profile = loginController.updateUserProfile(req.session.username, req.body);
//     res.render("user_profile.ejs", { user_profile: user_profile, successMessage: "Profile updated successfully", errorMessage: null });
// });

/**
 * Routes for Chat Query
 */

// app.post('/chat_query', async (req, res) => {
//     const query = req.body.query;
//     const username = req.session.username;
//     // Render chat page with query while response will process in the background
//     req.session.query_history.push(query);

//     const response = await loginController.chatQuery(query, username, req.session.query_history, req.session.response_history);
//     const marked_response = marked(response);
//     req.session.response_history.push(marked_response);

//     res.render("chat_page.ejs", { user_metrics: req.session.user_metrics, query_history: req.session.query_history, response_history: req.session.response_history, marked_response: marked_response, user_goals: req.session.user_goals });
// });

/**
 * Routes for My Devices Page
 */
// TODO: Understand why when I add a device after deleting a device - the add and delete actions are executed one after another
// app.post('/my_devices', async (req, res) => {

//     if(req.body.action == "add") {
//         const device_type = req.body.device_type;
//         const device_name = req.body.device_name;
//         const api_key = req.body.api_key;

//         const status = await loginController.addDevice(req.session.username, device_type, device_name, api_key);
//         if (status) {
//             // Reload the user's devices list
//             let user_devices = await loginController.getUserDevices(req.session.username);
//             res.render("my_devices_page.ejs", { user_devices: user_devices, successMessage: "Device added successfully", errorMessage: null });
//         } else {
//             res.render("my_devices_page.ejs", { successMessage: null, errorMessage: "Device addition failed" });
//         }
//     } else if(req.body.action == "delete") {
//         console.log("DELETE DEVICE");
//         const device_name = req.body.device_name;
//         const status = await loginController.deleteDevice(req.session.username, device_name);
//         console.log(status);
//         if (status) {
//             let user_devices = await loginController.getUserDevices(req.session.username);
//             res.render("my_devices_page.ejs", { user_devices: user_devices, successMessage: "Device deleted successfully", errorMessage: null });
//         }
//     }
// });

// app.post('/edit_device', (req, res) => {
//     const old_device_name = req.body.old_device_name;
//     const new_device_name = req.body.new_device_name;
//     const device_type = req.body.device_type;
//     const api_key = req.body.api_key;
//     const status = loginController.editDevice(req.session.username, old_device_name, new_device_name, device_type, api_key);

//     if (status) {
//         let user_devices = loginController.getUserDevices(req.session.username);
//         res.render("my_devices_page.ejs", { user_devices: user_devices, successMessage: "Device edited successfully", errorMessage: null });
//     } else {
//         res.render("my_devices_page.ejs", { successMessage: null, errorMessage: "Device editing failed" });
//     }
// });


/**
 * Routes for Navigation Bar
 */
// app.get('/logout', (req, res) => {
//     req.session.destroy();
//     res.redirect('/');
// });

// app.get('/my_devices', (req, res) => {
//     // Get the user deviecs list based on the session username
//     if (req.session.visited) {
//         // fetch user devices list from db
//         let user_devices = loginController.getUserDevices(req.session.username);
//         res.render("my_devices_page.ejs", { user_devices: user_devices});
//     } else {
//         res.redirect('/');
//     }
// });
