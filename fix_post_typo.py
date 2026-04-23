from app import create_app
from app.models import db, Post

app = create_app()
with app.app_context():
    # Update the specific post identified in the screenshot
    # We'll search by a partial title match to be safe
    post = Post.query.filter(Post.title.like('%How I Deployed a Second Site%')).first()
    
    if post:
        print(f"Found post: {post.title}")
        # Fix the content discrepancy: synchronize time to '5am' or 'midnight'
        # The screenshot shows '5am' in title and 'midnight' in body.
        # We'll align with the title since it's more prominent.
        if "midnight" in post.body.lower():
            post.body = post.body.replace("It was midnight.", "It was 5am.")
        
        # Fix the "Django construction" typo
        if "Django construction" in post.body:
            post.body = post.body.replace("Django construction", "Django project")
            print("Fixed 'Django construction' -> 'Django project'")
            
        db.session.commit()
        print("✅ Post updated successfully!")
    else:
        print("❌ Post not found. No changes made.")
