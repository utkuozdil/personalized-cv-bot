import boto3

# Local file path
file_path = 'Muammer_Utku_Ozdil_-_Senior_Software_Engineer_.pdf'

# S3 config
bucket_name = 'cv-chatbot-bucket-dev'
object_key = 'cv/Muammer_Utku_Ozdil_CV.pdf'  # Customize path/name

# Initialize S3 client
s3 = boto3.client('s3')

# 🛑 OPEN IN BINARY MODE!
with open(file_path, 'rb') as f:
    s3.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=f,
        ContentType='application/pdf'
    )

print("✅ Uploaded to S3 successfully.")
