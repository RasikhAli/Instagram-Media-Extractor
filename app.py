import os
from flask import Flask, render_template, send_file, request, Response, send_from_directory, stream_with_context
import instaloader
import requests
import zipfile
import io
import time
import urllib.parse
import json

app = Flask(__name__)

# Define the main media folder path
app.config['UPLOAD_FOLDER'] = 'static'

# Ensure the main upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/fetch_media', methods=['GET'])
def fetch_media():
    username = request.args.get('username')
    if username:
        return Response(stream_with_context(fetch_instagram_media(username)), mimetype='text/event-stream')
    return '', 204

@app.route('/proxy_image')
def proxy_image():
    # Get the URL from the request and ensure it's properly encoded
    image_url = request.args.get('url')
    if not image_url:
        return "Image URL is missing", 400

    try:
        # Decode and re-encode the URL to handle any improperly encoded characters
        decoded_url = urllib.parse.unquote(image_url)
        response = requests.get(decoded_url, stream=True)

        # Check if the request was successful
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', 'image/jpeg')

        return Response(response.content, content_type=content_type)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return f"Error fetching image: {str(e)}", 500

def fetch_instagram_media(username):
    loader = instaloader.Instaloader(download_videos=False, save_metadata=False)
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        # Add a 'profile_picture_proxy_url' to the profile data
        profile_data = {
            'name': profile.full_name,
            'username': profile.username,
            'profile_picture': profile.profile_pic_url,
            'profile_picture_proxy_url': f"/proxy_image?url={profile.profile_pic_url}",  # Updated line
            'followers': profile.followers,
        }

        # Send profile data first
        yield f"data: {json.dumps({'profile': profile_data})}\n\n"

        total_posts = profile.mediacount
        posts_loaded = 0

        # Fetch and send media
        for post in profile.get_posts():
            filename = download_media(post, profile.username, posts_loaded)
            media_data = {
                'title': post.caption if post.caption else "No Caption",
                'url': post.url,
                'date': post.date_utc.strftime('%Y-%m-%d'),
                'filename': filename
            }
            # Send media data
            yield f"data: {json.dumps({'media': media_data})}\n\n"
            posts_loaded += 1

            # Send the updated post count after each post is loaded
            post_info_data = {'total_posts': total_posts, 'posts_loaded': posts_loaded}
            yield f"data: {json.dumps({'post_info': post_info_data})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

def download_media(post, username, posts_loaded):
    # Create a subfolder for the username inside the media folder
    user_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(user_folder, exist_ok=True)  # Ensure the subfolder exists

    # Determine the media type
    media_type = 'jpg'  # Default to image
    if post.is_video:
        media_type = 'mp4'
    elif post.typename == 'GraphImage':
        media_type = 'jpg'
    elif post.typename == 'GraphVideo':
        media_type = 'mp4'
    elif post.typename == 'GraphSidecar':
        media_type = 'jpg'  # or 'mp4', handle accordingly for multiple media types

    # Construct the filename and file path for saving media
    # filename = f"{username}_{post.date_utc.strftime('%Y%m%d_%H%M%S')}.{media_type}"
    filename = f"{username}_{posts_loaded}.{media_type}"
    filepath = os.path.join(user_folder, filename)
    
    # Download the media if it hasn't already been downloaded
    if not os.path.exists(filepath):
        try:
            # Set the target to the user's subfolder
            loader = instaloader.Instaloader(download_videos=True, save_metadata=False)
            loader.download_post(post, target=user_folder)
            
            # Find the most recently downloaded file in the folder
            downloaded_files = [os.path.join(user_folder, f) for f in os.listdir(user_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4'))]
            latest_file = max(downloaded_files, key=os.path.getctime)

            # Rename the most recent file to match the desired filename
            os.rename(latest_file, filepath)
            
        except Exception as e:
            print(f"Failed to download or rename media: {e}")

    return filename  # Return the relative path for URL generation

@app.route('/download_all/<username>')
def download_all(username):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if not os.path.exists(user_folder):
        return 'User folder does not exist', 404

    # Create an in-memory zip file
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(user_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Add file to the zip file with relative path
                zipf.write(file_path, os.path.relpath(file_path, user_folder))
    
    zip_io.seek(0)  # Go to the start of the BytesIO object

    return send_file(
        zip_io,
        download_name=f'{username}_media.zip',
        as_attachment=True
    )

@app.route('/download/<path:filename>')
def download_file(filename):
    # The filename now includes the username subfolder, so it must be found correctly
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
