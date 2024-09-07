# Instagram Media Extractor

Instagram Media Extractor is a web-based application built with Flask that allows you to extract and download media from Instagram profiles. Simply input a username, and the app fetches profile information and media posts in real time, allowing you to view and download images and videos directly.

## Features
- **Profile Overview**: Displays profile picture, username, full name, and follower count.
- **Media Extraction**: Fetches and displays all media posts (images and videos) from the given Instagram profile.
- **Download Media**: Allows you to download individual media items directly.
- **Real-Time Updates**: Fetches posts in real-time and shows loaded post count.

## How It Works
1. Enter an Instagram username in the search bar.
2. The app will start fetching media posts in real time.
3. View media in a gallery format with options to download or view the original post on Instagram.
4. The Media Content is also saved locally (Without the download option) in the **static** folder.

## Installation
1. Clone this repository:
    ```bash
    git clone https://github.com/RasikhAli/instagram-media-extractor.git
    cd instagram-media-extractor
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the application:
    ```bash
    python app.py
    ```
4. Open your browser and navigate to `http://127.0.0.1:5000`.

## Screenshots
Include some screenshots of the app running to give users a visual overview.

## Future Improvements
- Bulk download all media with a single click.
- Add filters to sort media by date, type, or likes.
- Authentication for private profiles.

## Disclaimer
This tool is intended for educational and personal use only. Always respect Instagram’s terms of service and data privacy regulations.
