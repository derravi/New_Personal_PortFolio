# New Features: Review Moderation & Merged Analytics

This document describes the two major features added to the portfolio admin panel.

## 1. Project Review Moderation

### Overview
All project reviews submitted via the public API now require admin approval before being displayed to visitors. This gives you control over the quality and relevance of reviews shown on your project pages.

### How It Works

#### Review Statuses
Each review now has one of four statuses:
- **pending** - Newly submitted, awaiting review
- **approved** - Reviewed and approved, visible to public
- **hidden** - Reviewed but hidden (spam, spam-like, or off-topic)
- **deleted** - Permanently deleted from the system

#### Public API Changes
- **GET /api/projects/<slug>/reviews** - Now only returns reviews with `status = 'approved'`
- **POST /api/projects/<slug>/reviews** - New reviews are created with `status = 'pending'`

#### Admin Dashboard
Navigate to `/admin/reviews` to manage all submitted reviews.

**Features:**
- Filter reviews by status (All, Pending, Approved, Hidden)
- View reviewer name, rating, and comment
- Quick action buttons:
  - **Approve** - Mark review as approved (visible to public)
  - **Hide** - Mark review as hidden (spam, irrelevant, etc.)
  - **Delete** - Permanently delete the review

#### Database Schema
The `project_reviews` table now includes:
```sql
status TEXT DEFAULT 'pending' CHECK (status IN ('approved', 'pending', 'hidden', 'deleted'))
reviewed_at TEXT  -- When the review was moderated
reviewed_by TEXT  -- Admin email who reviewed it
```

#### Admin API Endpoints
```
GET /admin/api/reviews?status=pending
  - Get reviews, optionally filtered by status
  
PUT /admin/api/review/<id>/status
  - Update review status
  - Body: {"status": "approved|pending|hidden|deleted"}
  
DELETE /admin/api/review/<id>
  - Permanently delete a review
  
GET /admin/api/review-stats
  - Get review statistics
  - Returns: {
      "total": 10,
      "approved": 7,
      "pending": 2,
      "hidden": 1,
      "deleted": 0,
      "avg_rating": 4.5
    }
```

### User Experience

#### For Visitors
- Reviews displayed on project pages are guaranteed to be approved
- Reviews are moderated by the admin for quality and relevance
- They'll see a message like "This review is pending approval" if they try to view their own pending review

#### For Admin
- Dashboard widget shows quick stats: "Reviews Pending", "Reviews Approved"
- Dedicated reviews page with filtering and bulk actions
- Track who reviewed what and when

---

## 2. Analytics Merged Into Admin Dashboard

### Overview
The analytics dashboard is now integrated directly into the admin panel, accessible at `/admin/analytics`. You no longer need a separate token-based endpoint to view analytics—just log in with your admin credentials.

### How It Works

#### Access
- **Before:** `/analytics?token=YOUR_ADMIN_TOKEN` (token-based, not session-based)
- **Now:** `/admin/analytics` (session-based, requires admin login)

#### Dashboard Location
The analytics dashboard is now:
1. **Integrated into admin dashboard** - Quick stats on the main dashboard
2. **Full analytics page** - `/admin/analytics` for detailed view
3. **Sidebar link** - "Analytics" in the admin sidebar (with chart icon)

#### What's Included

**Key Metrics:**
- Total site visits
- Average response time (ms)
- Newsletter subscribers
- Contact messages received
- Project reviews (all statuses)
- Quiz attempts
- Top pages by traffic

**Recent Activity:**
- Last 50 page visits
- Request method, status code, duration
- Timestamp of each visit

#### Admin Dashboard Overview
The main admin dashboard now shows:
- Total projects, published, featured, views
- Total blog posts, published, views
- **NEW:** Reviews pending / approved
- **NEW:** Site visits

#### Admin API Endpoints
```
GET /admin/api/analytics
  - Get analytics data in JSON format
  - Returns full analytics object (same as page data)
  
GET /admin/analytics
  - HTML page with formatted analytics dashboard
```

### Benefits

1. **Single Login** - No need to manage separate tokens
2. **Better UX** - Session-based auth is more intuitive
3. **Integrated** - See analytics alongside other admin features
4. **Audit Trail** - Admin action logs show who accessed what
5. **Security** - Session-based auth with HTTP-only cookies

---

## Migration Guide

### For Existing Installations

If you're upgrading an existing installation:

1. **Database Migration** (automatic)
   - The system automatically adds new columns to `project_reviews`:
     - `status` (defaults to 'pending')
     - `reviewed_at`
     - `reviewed_by`
   - Existing reviews keep their current behavior (treated as pending)

2. **Review Existing Reviews** (manual)
   - Visit `/admin/reviews` to see all pending reviews
   - Approve reviews you want to display publicly
   - Hide or delete spam/irrelevant reviews

3. **Update Access Method** (optional)
   - Old `/analytics?token=...` endpoint still works
   - Switch to `/admin/analytics` for better experience
   - No change needed to external analytics consumers

---

## Technical Details

### Database Changes
```sql
-- Added to project_reviews table
ALTER TABLE project_reviews ADD COLUMN status TEXT DEFAULT 'pending';
ALTER TABLE project_reviews ADD COLUMN reviewed_at TEXT;
ALTER TABLE project_reviews ADD COLUMN reviewed_by TEXT;
```

### New Functions in admin_db.py
- `get_all_reviews(status='all')` - Get reviews, optionally filtered
- `get_reviews_by_project(slug, status='approved')` - Get approved reviews for a project
- `update_review_status(review_id, status, admin_email)` - Update review status
- `delete_review(review_id)` - Permanently delete review
- `get_review_stats()` - Get review statistics

### New Routes in admin_routes.py
- `GET /admin/reviews` - Reviews management page
- `GET /admin/analytics` - Analytics dashboard page
- `GET /admin/api/reviews` - API endpoint for all reviews
- `PUT /admin/api/review/<id>/status` - Update review status
- `DELETE /admin/api/review/<id>` - Delete review
- `GET /admin/api/review-stats` - Review statistics
- `GET /admin/api/analytics` - Analytics data (JSON)

### New Templates
- `templates/admin_reviews.html` - Reviews management interface
- `templates/admin_analytics.html` - Analytics dashboard

---

## FAQ

**Q: What happens to my existing reviews?**
A: Existing reviews will be treated as 'pending' until you approve them. Visitors won't see them until approved.

**Q: Can I still use the old token-based analytics endpoint?**
A: Yes, `/api/analytics/summary?token=...` still works and hasn't been removed.

**Q: How do I approve all reviews at once?**
A: Visit `/admin/reviews?status=pending` and use the "Approve" button on each review. For future bulk operations, this could be enhanced.

**Q: What if a user submits a review and it's approved later—are they notified?**
A: Not automatically. You could add email notifications in the future if needed.

**Q: Can I hide reviews without deleting them?**
A: Yes! The "Hidden" status lets you hide reviews without permanently deleting them. Hidden reviews can be unhidden later.

**Q: Does marking a review as hidden change the rating average?**
A: No, only 'approved' reviews count toward the public average rating shown to visitors.

**Q: Can I see who approved each review?**
A: Yes, the `reviewed_by` field stores the admin email who reviewed it, and `reviewed_at` stores the timestamp.

---

## Example Workflow

1. **User submits a review:**
   ```bash
   POST /api/projects/my-project/reviews
   {
     "name": "John Doe",
     "rating": 5,
     "comment": "Great project!"
   }
   ```
   → Review is created with `status = 'pending'`

2. **Admin is notified** (optional - could be added):
   - 1 pending review shows on dashboard

3. **Admin approves the review:**
   - Visits `/admin/reviews?status=pending`
   - Clicks "Approve" on John's review
   - Status changes to 'approved', `reviewed_at` and `reviewed_by` are set

4. **Review is now public:**
   - Visible on project page via `/api/projects/my-project/reviews`
   - Counts toward average rating
   - Visitors see "5 stars - Great project!"

5. **User can see their approved review:**
   - Listed publicly on the project page
   - Part of the overall rating calculation

---

## Future Enhancements

Potential improvements you could add:
- Email notifications for pending reviews
- Bulk approve/hide actions
- Automated spam detection
- Review replies from admin
- Review report/flag system
- Sentiment analysis for quality scoring
- Review export/analytics

---

**Last Updated:** July 2026
**Version:** 2.0
