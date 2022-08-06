from django.core.exceptions import ValidationError


def validate_file_size(file):
    """
    You use validators in the model to validate the data.
    """
    max_size_kb = 50

    if file.size > max_size_kb * 1024:
        raise ValidationError(f'File size must be less than {max_size_kb} KB')
