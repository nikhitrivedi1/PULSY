// Import required libraries
import axios from 'axios';

// Backend API endpoint configuration 
const API_BASE_URL = 'http://localhost:8000';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Controller class to handle API interactions, UI state management, and page routing
class LandingController {
    constructor() {
        this.isLoggedIn = false;
        this.errorMessage = '';
        this.queryResponse = '';
        this.currentPage = 'login'; // Track current page

        // Get directory path
        const __filename = fileURLToPath(import.meta.url);
        const __dirname = path.dirname(__filename);

        const server = http.createServer(async (req, res) => {
            if (req.url === '/') {
                try {
                    // Read the login page HTML file
                    const loginPagePath = path.join(__dirname, 'loginPage.html');
                    fs.readFile(loginPagePath, 'utf8', (err, data) => {
                        if (err) {
                            res.writeHead(500);
                            res.end('Error loading login page');
                            return;
                        }
                        res.writeHead(200, { 'Content-Type': 'text/html' });
                        res.end(data);
                    });
                } catch (err) {
                    res.writeHead(500);
                    res.end('Error loading login page');
                }
            } else {
                res.writeHead(404);
                res.end('Page not found');
            }
        });

        server.listen(8000, () => {
            console.log('Server is running on port 8000');
            console.log('Login page available at http://localhost:8000');
        });
    }

    // Page navigation methods
    async loadPage(pageName) {
        try {
            // Get directory path
            const __filename = fileURLToPath(import.meta.url);
            const __dirname = path.dirname(__filename);
            
            // Load HTML content
            const htmlPath = path.join(__dirname, `${pageName}.html`);
            const htmlContent = await fs.promises.readFile(htmlPath, 'utf8');
            
            // Load CSS stylesheet
            this.loadStylesheet(pageName);
            
            // Update DOM
            document.getElementById('main-content').innerHTML = htmlContent;
            
            this.currentPage = pageName;
            return true;
        } catch (err) {
            console.error(`Error loading page ${pageName}:`, err);
            return false;
        }
    }

    // Load page-specific CSS
    loadStylesheet(pageName) {
        // Remove existing page-specific stylesheet if exists
        const existingStylesheet = document.getElementById('page-specific-css');
        if (existingStylesheet) {
            existingStylesheet.remove();
        }

        // Add new stylesheet
        const stylesheet = document.createElement('link');
        stylesheet.id = 'page-specific-css';
        stylesheet.rel = 'stylesheet';
        stylesheet.type = 'text/css';
        stylesheet.href = `/styles/${pageName}.css`;
        document.head.appendChild(stylesheet);
    }

    // Page routing methods
    async navigateToLogin() {
        await this.loadPage('loginPage');
    }

    async navigateToDashboard() {
        if (this.isLoggedIn) {
            await this.loadPage('chat_page');
        } else {
            await this.navigateToLogin();
        }
    }

    async navigateToQuery() {
        if (this.isLoggedIn) {
            await this.loadPage('query');
        } else {
            await this.navigateToLogin();
        }
    }

    // Login controller method
    async handleLogin(username, password) {
        try {
            // const response = await axios.get(`${API_BASE_URL}/login/`, {
            //     params: {
            //         username: username,
            //         password: password
            //     }
            // });

            // response.data = "Success";
            
            if (true) {
                this.isLoggedIn = true;
                this.errorMessage = '';
                await this.navigateToDashboard();
                return {
                    success: true,
                    message: 'Login successful'
                };
            } else {
                this.errorMessage = response.data;
                return {
                    success: false,
                    message: response.data
                };
            }
        } catch (err) {
            this.errorMessage = 'Login failed. Please try again.';
            return {
                success: false,
                message: this.errorMessage
            };
        }
    }

    // Query controller method
    async handleQuery(queryText) {
        try {
            const response = await axios.post(`${API_BASE_URL}/query/`, {
                query: queryText
            });
            
            this.queryResponse = response.data;
            this.errorMessage = '';
            return {
                success: true,
                data: response.data
            };
        } catch (err) {
            this.errorMessage = 'Query failed. Please try again.';
            return {
                success: false,
                message: this.errorMessage
            };
        }
    }

    // Get current page
    getCurrentPage() {
        return this.currentPage;
    }

    // Get current login status
    getLoginStatus() {
        return this.isLoggedIn;
    }

    // Get current error message
    getErrorMessage() {
        return this.errorMessage;
    }

    // Get current query response
    getQueryResponse() {
        return this.queryResponse;
    }

    // Reset error message
    clearError() {
        this.errorMessage = '';
    }

    // Reset query response
    clearQueryResponse() {
        this.queryResponse = '';
    }

    // Logout method
    async logout() {
        this.isLoggedIn = false;
        this.errorMessage = '';
        this.queryResponse = '';
        await this.navigateToLogin();
    }
}

// Export controller instance
export const landingController = new LandingController();
