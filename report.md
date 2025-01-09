# Short report

Our project is a personal expense tracker designed as a web application implemented in Python using the Django framework. The purpose of this application is to help users efficiently manage their finances by tracking expenses and income, visualizing financial trends through charts, and organizing transactions by category. It is intended for individual users who wish to consolidate their financial data from multiple sources, such as credit cards and cash transactions, into a single, user-friendly platform.

The project consists of three primary components:
1. **Frontend Interface:** Built with HTML, CSS, and Bootstrap, it includes interactive elements supported by HTMX for dynamic content updates without requiring full-page reloads. The frontend allows users to navigate, input data, filter transactions, and view results seamlessly.
2. **Backend Logic:** Powered by Django, the backend manages user authentication, transaction records, filtering mechanisms, and database interactions. Key functionalities include CRUD operations for transactions, integration with filtering and exporting tools, and secure user management.
3. **Data Visualization:** Utilizing libraries like Plotly, the application provides interactive charts for users to analyze their income and expenses over time, categorized by month and type.

Throughout the development process, several challenges were encountered:
- **Dynamic Filtering and HTMX Integration:** While implementing real-time filtering, ensuring that dynamic updates did not duplicate or incorrectly overwrite content required careful coordination between the backend views and frontend templates.
- **User Feedback Handling:** Providing meaningful error messages during form validation, particularly for date fields, involved refining both backend validation and frontend error display logic.
- **Chart Customization:** Achieving user-friendly and visually appealing charts required significant customization of the Plotly library, such as displaying months by name (e.g., Jan, Feb) rather than numerical representations.

To overcome these hurdles, we adopted iterative testing and debugging approaches. For instance, issues with HTMX and partial templates were resolved by consolidating sidebar and content logic into reusable components. Similarly, CSS styles were centralized into an `index.css` file to ensure consistency and maintainability.

Future enhancements could include:
- **Bank Integration:** Streamlining data import by integrating APIs for popular banking services.
- **Mobile Responsiveness:** Optimizing the user interface for smaller devices to reach a broader audience.
- **Advanced Analytics:** Adding predictive analytics to provide users with insights into their spending patterns.

Despite some limitations, such as the lack of direct bank API integration, the application successfully provides a robust platform for users to track and manage their finances effectively. The lessons learned during development, particularly regarding dynamic content updates and user-centric design, will serve as valuable insights for future projects.

