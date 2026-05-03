#!/bin/bash
# Script для управления миграциями Alembic

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if alembic is installed
check_alembic() {
    if ! command -v alembic &> /dev/null; then
        print_error "Alembic is not installed. Installing..."
        pip install alembic
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [nsi|auth|rumor] <command> [options]"
    echo ""
    echo "Commands:"
    echo "  init              Initialize alembic (already done)"
    echo "  migrate MSG       Create a new migration with message"
    echo "  upgrade           Run all pending migrations"
    echo "  downgrade N       Downgrade N migrations"
    echo "  current           Show current migration"
    echo "  history           Show migration history"
    echo "  heads             Show current head(s)"
    echo "  stamp VERSION     Stamp database with version"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 nsi migrate 'Add players index'"
    echo "  $0 auth upgrade"
    echo "  $0 rumor upgrade"
    echo "  $0 nsi downgrade 1"
}

service="${1:-nsi}"
if [ "$service" = "nsi" ] || [ "$service" = "auth" ] || [ "$service" = "rumor" ]; then
    shift || true
else
    service="nsi"
fi

ALEMBIC_CONFIG="migrations/${service}_service/alembic.ini"

# Create new migration
create_migration() {
    local message="$1"
    if [ -z "$message" ]; then
        print_error "Migration message is required"
        echo "Usage: $0 migrate 'Your migration message'"
        exit 1
    fi
    print_info "Creating migration: $message"
    alembic -c "$ALEMBIC_CONFIG" revision --autogenerate -m "$message"
    print_info "Migration created successfully!"
}

# Run migrations
run_upgrade() {
    print_info "Running pending migrations..."
    alembic -c "$ALEMBIC_CONFIG" upgrade head
    print_info "Migrations completed successfully!"
}

# Downgrade migrations
run_downgrade() {
    local count="${1:-1}"
    print_warning "Downgrading $count migration(s)..."
    alembic -c "$ALEMBIC_CONFIG" downgrade -${count}
    print_info "Downgrade completed!"
}

# Show current migration
show_current() {
    print_info "Current migration:"
    alembic -c "$ALEMBIC_CONFIG" current
}

# Show migration history
show_history() {
    print_info "Migration history:"
    alembic -c "$ALEMBIC_CONFIG" history -v
}

# Show heads
show_heads() {
    print_info "Current head(s):"
    alembic -c "$ALEMBIC_CONFIG" heads
}

# Stamp database
stamp_db() {
    local version="$1"
    if [ -z "$version" ]; then
        print_error "Version is required"
        echo "Usage: $0 stamp <version>"
        exit 1
    fi
    print_info "Stamping database with version: $version"
    alembic -c "$ALEMBIC_CONFIG" stamp "$version"
}

# Main script
main() {
    check_alembic

    local command="${1:-help}"
    shift || true

    case "$command" in
        init)
            print_info "Alembic is already initialized"
            ;;
        migrate)
            create_migration "$1"
            ;;
        upgrade)
            run_upgrade
            ;;
        downgrade)
            run_downgrade "$1"
            ;;
        current)
            show_current
            ;;
        history)
            show_history
            ;;
        heads)
            show_heads
            ;;
        stamp)
            stamp_db "$1"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
