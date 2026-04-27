# Store 237 - Complete Python Retail Management Application

A comprehensive, production-ready retail management platform built with Python, Flask, and SQLAlchemy. Manage sales, inventory, expenses, team collaboration, and analytics all in one place.

## Features

### 🎨 User Interface
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Multi-Language Support** - English, French, Spanish, German, Portuguese, Chinese
- **Dark Mode** - Toggle between light and dark themes with persistent storage
- **Professional Branding** - Store 237 logo prominently displayed throughout

### 📊 Dashboard & Analytics
- Real-time KPI cards (Total Sales, Expenses, Profit/Loss)
- Profit margin percentage calculations (%gain, %loss)
- Expenses breakdown pie chart
- Best-selling products ranked bar chart
- Sales trend visualization over 30 days
- Multi-currency support (20+ currencies)

### 🛍️ Point of Sale (POS)
- Searchable product grid with images
- Shopping cart with quantity selectors
- Real-time profit calculations
- Receipt generation with profit/loss details
- PDF receipt export
- Transaction history

### 📦 Product Management
- Add/edit/delete products
- Image uploads with preview
- Cost price and selling price tracking
- Automatic profit margin calculation
- Stock level management
- Product categorization

### 💰 Financial Management
- Expense tracking by category
- Profit/loss calculations per transaction
- Profit margin percentage tracking
- Currency-aware financial reporting
- Professional PDF/CSV exports

### 👥 Team Collaboration
- Role-based access control (Admin, Manager, Viewer)
- Team member invitation system
- Role management
- Store-specific permissions
- Team member removal

### 🎮 Demo Account
- Pre-filled demo store with sample data
- 8 realistic products
- 10 sample sales transactions
- 6 expense categories
- Perfect for exploring all features
- Demo credentials: username: `demo`, password: `demo123`

## Installation

### Prerequisites
- Python 3.8+
- pip or poetry
- SQLite or PostgreSQL

### Setup

1. **Clone or extract the project**
```bash
cd store-237-python
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize database**
```bash
python3 -c "from app import create_app; app = create_app(); app.app_context().push()"
```

5. **Run application**
```bash
python3 app.py
```

The application will be available at `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///store237.db
UPLOAD_FOLDER=uploads
```

### Database

**SQLite (Default)**
```
DATABASE_URL=sqlite:///store237.db
```

**PostgreSQL**
```
DATABASE_URL=postgresql://user:password@localhost/store237
```

## Usage

### Demo Account
1. Go to landing page
2. Click "Test Demo" button
3. Explore all features with pre-filled data
4. Demo credentials: `demo` / `demo123`

### Create Your Store
1. Click "Get Started Free"
2. Fill in registration form
3. Create your store with name, proprietor, and seller information
4. Start managing your retail business

### Key Workflows

**Adding Products**
1. Navigate to Products
2. Click "Add Product"
3. Enter product details
4. Upload product image
5. Set cost and selling prices
6. Save

**Processing Sales**
1. Go to POS
2. Search for products
3. Add to cart with quantities
4. Review profit calculations
5. Checkout
6. Generate receipt

**Tracking Expenses**
1. Navigate to Expenses
2. Click "Add Expense"
3. Select category
4. Enter amount
5. Add description
6. Save

**Managing Team**
1. Go to Team
2. Click "Invite Member"
3. Enter email and select role
4. Member receives invitation
5. Manage roles and permissions

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/demo_login` - Demo account login
- `GET /auth/logout` - User logout

### Dashboard
- `GET /dashboard/` - Dashboard page
- `GET /dashboard/api/kpis/<store_id>` - KPI data
- `GET /dashboard/api/expenses-breakdown/<store_id>` - Expenses breakdown
- `GET /dashboard/api/best-selling-products/<store_id>` - Best sellers
- `GET /dashboard/api/sales-trend/<store_id>` - Sales trend

### Products
- `GET /products/` - Product list
- `POST /products/create` - Create product
- `POST /products/<id>/edit` - Edit product
- `POST /products/<id>/delete` - Delete product
- `GET /products/api/list/<store_id>` - API product list

### Sales
- `GET /sales/pos` - POS interface
- `POST /sales/api/checkout` - Process checkout
- `GET /sales/receipt/<receipt_id>/pdf` - Generate PDF receipt
- `GET /sales/history` - Sales history
- `GET /sales/api/history/<store_id>` - API sales history

### Expenses
- `GET /expenses/` - Expense list
- `POST /expenses/create` - Create expense
- `POST /expenses/<id>/delete` - Delete expense
- `GET /expenses/api/list/<store_id>` - API expense list

### Team
- `GET /team/` - Team members
- `POST /team/invite` - Invite member
- `POST /team/<id>/role` - Update role
- `POST /team/<id>/remove` - Remove member
- `GET /team/api/list/<store_id>` - API team list

### Settings
- `GET /settings/` - Settings page
- `POST /settings/store/<id>` - Update store
- `POST /settings/profile` - Update profile
- `GET /settings/api/store/<id>` - API store settings

## Database Schema

### Users
- id, username, email, password_hash, full_name, is_demo, created_at, updated_at

### Stores
- id, store_id, store_name, proprietor_name, seller_name, owner_id, currency, description, logo_url, created_at, updated_at

### Products
- id, product_id, store_id, name, description, cost_price, selling_price, quantity_in_stock, image_url, category, created_at, updated_at

### Sales
- id, sale_id, store_id, product_id, quantity, unit_price, total_amount, cost_total, profit, profit_margin_percent, seller_name, created_at

### Expenses
- id, expense_id, store_id, category, amount, description, created_at

### TeamMembers
- id, user_id, store_id, role, joined_at

### Receipts
- id, receipt_id, store_id, items (JSON), total_amount, total_cost, total_profit, profit_margin_percent, created_at

### RecurringReports
- id, store_id, frequency, email, enabled, last_sent, created_at

## Deployment

### Heroku
```bash
heroku create store-237
git push heroku main
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
```

### Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:create_app()"]
```

### Traditional Server
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## Security Considerations

- Always set a strong `SECRET_KEY` in production
- Use HTTPS in production
- Enable `SESSION_COOKIE_SECURE` for production
- Regularly backup your database
- Use environment variables for sensitive data
- Implement rate limiting for API endpoints
- Validate all user inputs
- Use parameterized queries (SQLAlchemy handles this)

## Troubleshooting

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"
```

### Port Already in Use
```bash
# Use different port
python3 app.py --port 5001
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Performance Optimization

- Enable database query caching
- Use pagination for large datasets
- Implement image compression
- Add database indexes on frequently queried columns
- Use CDN for static assets in production
- Enable gzip compression

## Future Enhancements

- SMS notifications for low stock alerts
- Email report scheduling with background jobs
- Advanced inventory forecasting
- Customer loyalty programs
- Mobile app (React Native)
- API rate limiting
- Advanced analytics and reporting
- Multi-store dashboard
- Barcode/QR code scanning
- Integration with payment gateways

## Support & Documentation

For issues, feature requests, or documentation, please visit the project repository.

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Credits

Built with:
- Flask - Web framework
- SQLAlchemy - ORM
- Babel - Internationalization
- ReportLab - PDF generation
- Pillow - Image processing

---

**Store 237** - Retail Management Made Simple

Version: 1.0.0
Last Updated: April 2024
