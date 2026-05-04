import os
from pathlib import Path
from datetime import datetime

def should_include_file(file_path):
    """
    Determine if a file should be included in the documentation.
    """
    # Files to exclude
    exclude_patterns = [
        '.pyc',
        '.pyo',
        '.pyd',
        '__pycache__',
        '.git',
        '.pytest_cache',
        '.coverage',
        '.env',  # Exclude actual env file for security
        '.vscode',
        '.idea',
        'venv',
        'env',
        '.DS_Store',
        'Thumbs.db'
    ]
    
    # Check if any exclude pattern is in the path
    path_str = str(file_path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return False
    
    # Include these file types
    include_extensions = [
        '.py',
        '.md',
        '.txt',
        '.yml',
        '.yaml',
        '.json',
        '.env.example',
        'Dockerfile',
        '.gitignore',
        'requirements.txt',
        'README.md'
    ]
    
    # Check if file has an included extension or is a special file
    file_name = os.path.basename(path_str)
    if file_name in ['Dockerfile', '.gitignore', 'requirements.txt', 'README.md', '.env.example']:
        return True
    
    for ext in include_extensions:
        if path_str.endswith(ext):
            return True
    
    return False

def get_language_for_file(file_path):
    """
    Get the appropriate language identifier for syntax highlighting.
    """
    extension_map = {
        '.py': 'python',
        '.md': 'markdown',
        '.txt': 'text',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.json': 'json',
        '.env.example': 'bash',
        'Dockerfile': 'dockerfile',
        '.gitignore': 'gitignore',
        'requirements.txt': 'text'
    }
    
    file_name = os.path.basename(file_path)
    
    # Check special files first
    if file_name in ['Dockerfile', '.gitignore', 'requirements.txt']:
        return extension_map.get(file_name, 'text')
    
    # Check by extension
    _, ext = os.path.splitext(file_path)
    return extension_map.get(ext, 'text')

def compile_backend_documentation(root_dir, output_file='backend_documentation.md'):
    """
    Compile all backend code into a single markdown file.
    
    Args:
        root_dir: The root directory of the backend project
        output_file: The output markdown file name
    """
    root_path = Path(root_dir)
    
    # Create the markdown content
    markdown_content = []
    
    # Add header
    markdown_content.append("# Backend Project Documentation\n")
    markdown_content.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    markdown_content.append(f"**Project Root:** `{root_dir}`\n")
    markdown_content.append("\n---\n\n")
    
    # Add table of contents
    markdown_content.append("## Table of Contents\n\n")
    toc_entries = []
    
    # First pass: collect all files for TOC
    all_files = []
    for root, dirs, files in os.walk(root_path):
        # Remove __pycache__ from dirs to prevent walking into it
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            file_path = Path(root) / file
            if should_include_file(file_path):
                relative_path = file_path.relative_to(root_path)
                all_files.append((file_path, relative_path))
    
    # Sort files by path for better organization
    all_files.sort(key=lambda x: str(x[1]))
    
    # Group files by directory
    current_dir = None
    for _, relative_path in all_files:
        dir_path = relative_path.parent
        
        # Add directory header if changed
        if dir_path != current_dir:
            current_dir = dir_path
            dir_name = str(dir_path) if str(dir_path) != '.' else 'Root'
            toc_entries.append(f"- **{dir_name}/**")
        
        # Add file to TOC
        anchor = str(relative_path).replace('/', '-').replace('\\', '-').replace('.', '').lower()
        toc_entries.append(f"  - [{relative_path.name}](#{anchor})")
    
    markdown_content.append('\n'.join(toc_entries))
    markdown_content.append("\n\n---\n\n")
    
    # Second pass: add file contents
    markdown_content.append("## File Contents\n\n")
    
    current_dir = None
    for file_path, relative_path in all_files:
        dir_path = relative_path.parent
        
        # Add directory section if changed
        if dir_path != current_dir:
            current_dir = dir_path
            dir_name = str(dir_path) if str(dir_path) != '.' else 'Root'
            markdown_content.append(f"### 📁 {dir_name}\n\n")
        
        # Add file content
        anchor = str(relative_path).replace('/', '-').replace('\\', '-').replace('.', '').lower()
        markdown_content.append(f"#### 📄 {relative_path.name}\n")
        markdown_content.append(f"**Path:** `{relative_path}`\n\n")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Get language for syntax highlighting
            language = get_language_for_file(str(file_path))
            
            # Add code block
            markdown_content.append(f"```{language}\n")
            markdown_content.append(content)
            if not content.endswith('\n'):
                markdown_content.append('\n')
            markdown_content.append("```\n\n")
            
        except Exception as e:
            markdown_content.append(f"❌ **Error reading file:** {e}\n\n")
        
        markdown_content.append("---\n\n")
    
    # Add footer
    markdown_content.append("## Summary\n\n")
    markdown_content.append(f"**Total files documented:** {len(all_files)}\n\n")
    
    # Count by file type
    file_types = {}
    for _, relative_path in all_files:
        ext = relative_path.suffix or relative_path.name
        file_types[ext] = file_types.get(ext, 0) + 1
    
    markdown_content.append("**Files by type:**\n")
    for ext, count in sorted(file_types.items()):
        markdown_content.append(f"- {ext}: {count}\n")
    
    markdown_content.append("\n---\n")
    markdown_content.append(f"\n*Documentation generated by automated script on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Write to file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(markdown_content))
    
    print(f"✅ Documentation successfully generated: {output_path.absolute()}")
    print(f"📊 Total files documented: {len(all_files)}")
    print(f"📄 Output file size: {output_path.stat().st_size / 1024:.2f} KB")

def main():
    # Set the root directory of your backend project
    backend_root = r"D:\NexusNao\CLIENTS\BAKAR\backend"
    
    # Set the output file path (will be created in the current directory)
    output_file = "backend_documentation.md"
    
    # You can also specify an absolute path for the output
    # output_file = r"D:\NexusNao\CLIENTS\BAKAR\backend_documentation.md"
    
    # Run the documentation compiler
    compile_backend_documentation(backend_root, output_file)

if __name__ == "__main__":
    main()
