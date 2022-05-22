import os

def get_unreal_format_path(abspath, project_path):
    if os.path.relpath(abspath, project_path).startswith(os.pardir):
        print("Absolute path is not a subpath of the project path!")
        return abspath
    content_path = os.path.join(project_path, 'Content')
    relative_path = os.path.relpath(abspath, content_path)
    return os.path.join('/Game', relative_path).replace(os.sep, '/')
