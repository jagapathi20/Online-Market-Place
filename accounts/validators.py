from django.core.exceptions import ValidationError
import os

def validate_file_extension(file):
    ext = os.path.splitext(file.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('File extension must be jpg, jpeg, png')

def validate_file_size(file):
    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError('File size must be less than 5MB')
    return file