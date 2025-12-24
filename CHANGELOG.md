# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-22

### Added
- **Portmanteau Tools Architecture**: Consolidated 28 individual tools into 15 portmanteau tools
  - `avatar_manager`: Comprehensive avatar lifecycle management (load, unload, list, set_active, get_active, get_metadata)
  - `animation_controller`: Animation control and management (play, stop, list)
  - `osc_communicator`: OSC communication hub (send, receive)
  - `unity_integration`: Unity desktop avatar control (status, load_avatar, set_expression, control_animation)
  - `chat_manager`: Chat session management (start_session, send_message, stop_session, get_state)
  - `system_monitor`: System health and diagnostics (get_status, get_health, get_metrics)
- **FastMCP 2.12 Standards Compliance**: All tools follow FastMCP 2.12 standards with multiline docstrings
- **Real Tool Implementations**: All core tools now have actual working functionality instead of mock responses
- **Unity Desktop Integration**: Full Unity desktop avatar control with OSC communication
- **Chat System**: Interactive chatbot functionality with session management
- **System Monitoring**: Comprehensive system health and diagnostics with performance metrics
- **MCPB Packaging**: Production-ready MCPB package with proper configuration
- **Comprehensive Error Handling**: Robust error handling throughout all tools
- **Type Annotations**: Full type hints throughout the codebase

### Changed
- **Architecture Refactoring**: Moved from individual tool handlers to modular portmanteau tool classes
- **Tool Count Reduction**: Reduced from 28 individual tools to 15 consolidated portmanteau tools (47% reduction)
- **Code Organization**: Clean separation of concerns with focused tool classes
- **Documentation**: Updated README and documentation to reflect new architecture
- **Linting**: Switched from black to ruff for faster, more comprehensive linting
- **Server Structure**: Cleaned up server.py by moving tool logic to dedicated classes

### Fixed
- **Ruff Linting Errors**: Fixed all 47 linting errors including line length and duplicate exception blocks
- **Test Failures**: Fixed all failing tests including API integration tests and avatar MCP tests
- **Import Issues**: Resolved all import and module loading issues
- **Mock Tool Issues**: Replaced all mock implementations with real, working functionality
- **Error Handling**: Improved error handling and logging throughout the system

### Removed
- **Mock Implementations**: Removed all mock tool implementations in favor of real functionality
- **Bloated Server Code**: Removed large tool implementations from server.py
- **Deprecated Tools**: Consolidated deprecated individual tools into portmanteau tools

## [0.1.0] - 2025-10-21

### Added
- Initial release
- Core functionality implemented
- Documentation created

### Changed
- N/A

### Fixed
- N/A

### Removed
- N/A

---

## How to Update This File

When making changes, add them under the appropriate section:
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
