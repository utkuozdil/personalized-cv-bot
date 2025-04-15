from datetime import datetime

def get_confirm_response(item):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resume Confirmed</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                                 Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    background-color: #f9f9f9;
                    color: #212529;
                    padding: 40px;
                }}
                .card {{
                    background: white;
                    padding: 32px;
                    margin: 0 auto;
                    max-width: 520px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    text-align: center;
                }}
                h2 {{
                    margin-top: 0;
                    color: #4CAF50;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .footer {{
                    color: #999;
                    font-size: 12px;
                    margin-top: 24px;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>✅ Resume Confirmed</h2>
                <p>The resume for <strong>{item['email']}</strong> has been successfully confirmed.</p>
                <p>Processing has started. Thank you!</p>
                <div class="footer">
                    &copy; {datetime.now().year} Resume Assistant
                </div>
            </div>
        </body>
        </html>
        """
    }

def get_mail_template(email, filename, confirm_link):
    return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Resume Uploaded</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                                 Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    background-color: #ffffff;
                    color: #212529;
                    padding: 40px;
                    margin: 0;
                    line-height: 1.5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    text-align: left;
                }}
                h2 {{
                    margin: 0 0 24px 0;
                    font-size: 24px;
                    font-weight: 600;
                    color: #212529;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .icon {{
                    color: #6c757d;
                    font-size: 20px;
                }}
                .field {{
                    margin: 16px 0;
                    color: #212529;
                }}
                .field a {{
                    color: #0d6efd;
                    text-decoration: none;
                }}
                .field-label {{
                    font-weight: 500;
                    margin-right: 8px;
                }}
                .filename {{
                    color: #495057;
                }}
                .button {{
                    display: inline-flex;
                    align-items: center;
                    padding: 8px 16px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-size: 14px;
                    margin: 24px 0;
                    border: none;
                    cursor: pointer;
                }}
                .button .check {{
                    margin-right: 8px;
                }}
                .footer {{
                    color: #6c757d;
                    font-size: 14px;
                    margin-top: 16px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2><span class="icon">📄</span> New Resume Uploaded</h2>
                
                <div class="field">
                    <span class="field-label">Email:</span>
                    <a href="mailto:{email}">{email}</a>
                </div>

                <div class="field">
                    <span class="field-label">Filename:</span>
                    <span class="filename">{filename}</span>
                </div>

                <a href="{confirm_link}" class="button">
                    <span class="check">✓</span>
                    Confirm Resume
                </a>

                <div class="footer">
                    This action is required before the resume is processed.
                </div>
            </div>
        </body>
        </html>
    """
