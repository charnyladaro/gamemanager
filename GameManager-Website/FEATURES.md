# GameManager Features

Complete feature list for the GameManager application.

## 🏪 Store & Marketplace

### Game Store
- Browse curated collection of free and premium games
- High-quality game cover images automatically fetched
- Detailed game information (description, genre, developer, publisher, file size)
- Search and filter games
- View game prices in Philippine Peso (₱)

### Pricing
- **Free Games**: Add directly to library with one click
- **Paid Games**: Affordable prices typically ranging from ₱50-₱200
- Transparent pricing with no hidden fees
- Flexible pricing model for different game types

### Purchase Process
- Secure GCash payment integration
- Step-by-step payment instructions
- Submit GCash reference number for verification
- Real-time payment status tracking
- Automatic library addition upon approval

## 💳 Payment System

### GCash Integration
- Easy payment submission process
- Reference number tracking
- Payment verification by admins
- Secure transaction handling

### Payment History
- View all purchase transactions
- Track payment status (Pending, Completed, Failed)
- See GCash reference numbers
- Download payment receipts
- Filter by status and date

### Payment Statuses
- **Pending Verification**: Awaiting admin approval
- **Completed**: Payment verified, game added to library
- **Failed**: Payment rejected or invalid

## 📚 Library Management

### Personal Library
- Beautiful grid view of owned games
- Automatic cover artwork display
- Installation status tracking
- Playtime tracking and statistics
- Last played information
- Quick launch access

### Library Features
- Add/remove games
- Mark games as installed
- Track download progress
- View game details
- Sort and filter options

## 👥 Social Features

### Friends System
- Send and receive friend requests
- View friends list
- See online/offline status
- Real-time status updates
- Remove friends option

### Friend Management
- Search users by username
- Pending request notifications
- Accept/reject friend requests
- View sent requests

### Social Integration
- See what friends are playing
- Share gaming experiences
- Connect with gaming community

## 🎯 Game Requests

### Request System
- Request new games to be added to store
- Provide game title and description
- Track request status
- Admin review and feedback
- Status updates (Pending, Approved, Rejected)

### User Benefits
- Influence store catalog
- Vote for desired games
- Community-driven content
- Direct communication with admins

## 🖼️ Cover Artwork System

### Automatic Cover Fetch
- Integration with RAWG Video Games Database API
- High-quality cover images
- Automatic title matching
- Background image support
- Fallback placeholder images

### Admin Tools
- Bulk cover fetch for multiple games
- Manual cover upload option
- Cover image management
- Replace/update covers

## 🔍 Game Scanner

### Auto-Detection
- Scan folders for game files
- Automatically extract game titles from filenames
- Detect file metadata (size, type, date)
- Suggest game titles
- Process multiple files at once

### Supported Formats
- `.exe` - Executable files
- `.msi` - Windows Installer packages
- `.zip` - Compressed archives
- `.rar` - RAR archives
- `.7z` - 7-Zip archives

### Smart Title Extraction
- Remove version numbers
- Clean up file separators
- Remove common tags (REPACK, CODEX, etc.)
- Apply proper capitalization
- Handle special characters

## 🔒 Admin Dashboard

### User Management
- View all registered users
- User statistics (games owned, friends, playtime)
- Edit user information
- Grant/revoke admin privileges
- Delete users
- Create new users
- Search and filter users

### Game Management
- View all games in store
- Add new games manually or from scanned files
- Edit game information (title, description, price, etc.)
- Toggle game availability
- Delete games
- Upload cover images
- Set game prices

### Payment Verification
- Review pending payments
- Verify GCash reference numbers
- Approve/reject payments
- View payment history
- Track transaction details
- Monitor revenue

### Game Request Management
- View all game requests
- Filter by status (Pending, Approved, Rejected)
- Approve or reject requests
- Add admin notes
- Track request history
- Respond to users

### Analytics Dashboard
- Total users count
- Online users
- Total games
- Total downloads
- Revenue statistics
- User engagement metrics
- Recent activity feed

### Scanned Games Management
- View auto-detected games
- Edit suggested titles
- Fetch cover images
- Move to library/store
- Delete scanned entries
- Batch operations

## 🔐 Authentication & Security

### User Authentication
- Secure registration system
- JWT token-based authentication
- Password hashing (Werkzeug)
- Session management
- Auto-logout on token expiration

### Security Features
- Encrypted passwords
- Secure API endpoints
- Admin-only routes protection
- CORS configuration
- Input validation
- SQL injection prevention

## ⚙️ Technical Features

### Backend (Flask/Python)
- RESTful API architecture
- SQLite database
- SQLAlchemy ORM
- JWT authentication
- File upload handling
- Image processing
- CORS support

### Frontend (Electron)
- Modern UI with dark theme
- Responsive design
- Real-time updates
- Toast notifications
- Modal dialogs
- Loading states
- Error handling

### Performance
- Fast load times
- Optimized database queries
- Efficient file handling
- Lazy loading
- Caching mechanisms
- Background operations

## 📊 User Features

### Profile Management
- Update display name
- Change password
- View account statistics
- Privacy settings
- Account deletion option

### Notifications
- Payment status updates
- Friend requests
- Game request updates
- Download completion
- System notifications

### Settings
- Theme customization
- Notification preferences
- Privacy controls
- Language options (future)
- Download location

## 🎮 Gaming Features

### Game Launch
- Quick launch from library
- Recently played games
- Favorite games
- Play history

### Statistics Tracking
- Total playtime per game
- Last played date
- Most played games
- Gaming achievements (future)

## 🚀 Future Features (Planned)

- Multiple payment methods (PayMaya, credit card)
- Game reviews and ratings
- User profiles with avatars
- In-app chat with friends
- Game categories and tags
- Advanced search filters
- Wishlist functionality
- Sale and discount system
- Achievements and badges
- Cloud save support
- Game streaming integration
- Mobile app companion

## 📱 Platform Support

### Current
- Windows 10 (64-bit)
- Windows 11 (64-bit)

### Planned
- macOS support
- Linux support
- Mobile apps (iOS/Android)

## 🌐 Localization

### Current
- English interface
- Philippine Peso (₱) currency
- Philippines-focused features

### Planned
- Filipino/Tagalog language
- Multiple currency support
- Regional pricing
- Time zone support

## 💡 Highlights

### Why Choose GameManager?

1. **All-in-One Solution**: Store, library, and social features in one app
2. **Local Payment Support**: GCash integration for easy purchases
3. **Affordable Games**: Low prices tailored for Philippine market
4. **Free to Use**: No subscription fees or hidden costs
5. **Beautiful Interface**: Modern, Steam-like user experience
6. **Community-Driven**: Game requests influence store catalog
7. **Secure**: Encrypted data and secure payments
8. **Lightweight**: Fast and efficient performance
9. **Regular Updates**: Continuous improvements and new features
10. **Admin Support**: Responsive admin team for verification

---

**Last Updated**: November 2024
**Version**: 1.0.0
