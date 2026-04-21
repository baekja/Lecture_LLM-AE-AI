#!/bin/bash

# RAG System Installation Script
# Supports macOS and Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="${HOME}/.local/rag-system"
BIN_DIR="${HOME}/.local/bin"
VENV_DIR="${INSTALL_DIR}/venv"

echo "======================================"
echo "    RAG System Installation Script    "
echo "======================================"
echo ""

# Check Python version
check_python() {
    echo "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
            return 0
        else
            echo -e "${RED}✗${NC} Python 3.8+ required (found $PYTHON_VERSION)"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} Python 3 not found"
        return 1
    fi
}

# Create installation directory
create_directories() {
    echo "Creating installation directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$INSTALL_DIR/docs/originals"
    mkdir -p "$INSTALL_DIR/knowledge/md"
    mkdir -p "$INSTALL_DIR/knowledge/index"
    mkdir -p "$INSTALL_DIR/scratch"
    
    echo -e "${GREEN}✓${NC} Directories created"
}

# Copy application files
copy_files() {
    echo "Copying application files..."

    # Get the script directory (current package directory)
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    # In distribution package, PROJECT_ROOT is the same as SCRIPT_DIR
    # Check if we're in a distribution package or development environment
    if [ -d "$SCRIPT_DIR/scripts" ]; then
        # Distribution package structure
        PROJECT_ROOT="$SCRIPT_DIR"
    else
        # Development environment structure
        PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    fi

    # Copy scripts
    if [ -d "$PROJECT_ROOT/scripts" ]; then
        cp -r "$PROJECT_ROOT/scripts" "$INSTALL_DIR/"
    else
        echo -e "${RED}✗${NC} scripts directory not found in $PROJECT_ROOT"
        return 1
    fi

    # Copy main application file
    if [ -f "$PROJECT_ROOT/rag_system.py" ]; then
        cp "$PROJECT_ROOT/rag_system.py" "$INSTALL_DIR/"
    elif [ -f "$SCRIPT_DIR/rag_system.py" ]; then
        cp "$SCRIPT_DIR/rag_system.py" "$INSTALL_DIR/"
    else
        echo -e "${RED}✗${NC} rag_system.py not found"
        return 1
    fi

    # Copy requirements
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        cp "$PROJECT_ROOT/requirements.txt" "$INSTALL_DIR/"
    else
        echo -e "${RED}✗${NC} requirements.txt not found"
        return 1
    fi

    # Copy documentation (optional)
    if [ -f "$PROJECT_ROOT/README.md" ]; then
        cp "$PROJECT_ROOT/README.md" "$INSTALL_DIR/"
    fi

    if [ -f "$PROJECT_ROOT/CLAUDE.md" ]; then
        cp "$PROJECT_ROOT/CLAUDE.md" "$INSTALL_DIR/"
    fi

    echo -e "${GREEN}✓${NC} Files copied"
    return 0
}

# Create virtual environment
create_venv() {
    echo "Creating Python virtual environment..."
    
    python3 -m venv "$VENV_DIR"
    
    echo -e "${GREEN}✓${NC} Virtual environment created"
}

# Install dependencies
install_dependencies() {
    echo "Installing Python dependencies..."
    echo "This may take a few minutes..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    echo "  - Upgrading pip..."
    if ! pip install --upgrade pip > /dev/null 2>&1; then
        echo -e "${YELLOW}!${NC} Failed to upgrade pip, continuing with existing version"
    fi

    # Install requirements
    echo "  - Installing packages from requirements.txt..."
    if ! pip install -r "$INSTALL_DIR/requirements.txt"; then
        echo -e "${RED}✗${NC} Failed to install dependencies"
        echo "Please check your internet connection and try again"
        deactivate
        return 1
    fi

    deactivate

    echo -e "${GREEN}✓${NC} Dependencies installed successfully"
    return 0
}

# Create executable wrapper
create_wrapper() {
    echo "Creating executable wrapper..."
    
    cat > "$BIN_DIR/rag-system" << 'EOF'
#!/bin/bash
INSTALL_DIR="${HOME}/.local/rag-system"
VENV_DIR="${INSTALL_DIR}/venv"

# Activate virtual environment and run
source "${VENV_DIR}/bin/activate"
cd "${INSTALL_DIR}"
python rag_system.py "$@"
deactivate
EOF
    
    chmod +x "$BIN_DIR/rag-system"
    
    echo -e "${GREEN}✓${NC} Executable created"
}

# Update shell configuration
update_shell_config() {
    echo "Updating shell configuration..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    case "$SHELL_NAME" in
        bash)
            CONFIG_FILE="$HOME/.bashrc"
            ;;
        zsh)
            CONFIG_FILE="$HOME/.zshrc"
            ;;
        *)
            CONFIG_FILE="$HOME/.profile"
            ;;
    esac
    
    # Add to PATH if not already there
    if ! grep -q "/.local/bin" "$CONFIG_FILE" 2>/dev/null; then
        echo "" >> "$CONFIG_FILE"
        echo "# RAG System" >> "$CONFIG_FILE"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$CONFIG_FILE"
        echo -e "${GREEN}✓${NC} PATH updated in $CONFIG_FILE"
    else
        echo -e "${YELLOW}!${NC} PATH already configured"
    fi
}

# Main installation
main() {
    echo ""
    
    # Check Python
    if ! check_python; then
        echo -e "${RED}Installation failed: Python 3.8+ required${NC}"
        echo "Please install Python 3.8 or higher and try again"
        exit 1
    fi
    
    echo ""
    
    # Create directories
    create_directories
    
    # Copy files
    if ! copy_files; then
        echo -e "${RED}Installation failed during file copy${NC}"
        echo "Please check that all required files are present in the package"
        exit 1
    fi
    
    # Create virtual environment
    create_venv
    
    # Install dependencies
    if ! install_dependencies; then
        echo -e "${RED}Installation failed during dependency installation${NC}"
        echo "You can try installing dependencies manually later with:"
        echo "  source $VENV_DIR/bin/activate"
        echo "  pip install -r $INSTALL_DIR/requirements.txt"
        exit 1
    fi
    
    # Create wrapper
    create_wrapper
    
    # Update shell config
    update_shell_config
    
    echo ""
    echo "======================================"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo "======================================"
    echo ""
    echo "To get started:"
    echo "1. Reload your shell: source ~/.bashrc (or ~/.zshrc)"
    echo "2. Add documents to: $INSTALL_DIR/docs/originals/"
    echo "3. Run setup: rag-system setup"
    echo "4. Search: rag-system search 'your query'"
    echo ""
    echo "For help: rag-system --help"
    echo ""
}

# Run main installation
main