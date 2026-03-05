# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Web UI (web_sota)**: Resolved Vite pre-transform errors on dev startup.
  - Added missing `APPS_CATALOG` export in `src/common/apps-catalog.ts` (alias for `FLEET_REGISTRY`) for topbar/layout imports.
  - Added `framer-motion` dependency for `FleetCard.tsx` and other animated components.
  - Frontend now starts cleanly on port 10792 with backend proxy to 10793.

---

## [1.2.0] - 2026-02-24

### Added
- **New Portmanteau Managers**: Consolidated all remaining tools into professional manager interfaces:
  - `emotion_manager`: Unified emotion, micro-expressions, and personality profiles.
  - `audio_manager`: Unified audio playback and singing synthesis.
  - `behavior_manager`: Unified AI conversation, adaptation, and learning behaviors.
  - `animation_manager`: Unified animation play/stop, sequences, and layering.
  - `collaboration_manager`: Unified multi-user sync and session management.
  - `content_manager`: Unified asset creation, listing, and publishing.
  - `interaction_manager`: Unified tactical triggers and interactive gestures.
  - `performance_manager`: Unified VRM optimization and profiling.

### Changed
- **Architecture Refactoring**: Complete purge of redundant tools and bridge logic in `server.py`.
- **Fleet Alignment**: Removed OSC and Resonite-specific tools now handled by dedicated fleet servers.
- **Portmanteau Consolidation**: Reduced tool footprint by 50% while maintaining full feature parity.

### Fixed
- **Registration Errors**: Resolved `NameError` in `server.py` and improved modular tool loading.

---


### Added
- **Agentic Sampling Workflows**: Revolutionary FastMCP 2.14.3 sampling capabilities (SEP-1577)
  - `avatar_sampling`: New portmanteau tool for agentic avatar orchestration
  - LLM-driven autonomous workflow execution without manual sequencing
  - Intelligent choreography with emotional intelligence and timing control
  - Available operations: load_avatar, play_animation, set_morph, control_bone, send_osc, set_emotion, create_sequence, blend_animations, get_status, wait
- **16th Portmanteau Tool**: Expanded from 15 to 16 tools with sampling capabilities
- **Sampling Workflow Examples**: Comprehensive examples for emotional performances, dance choreography, and interactive storytelling
- **Advanced Usage Tips**: Best practices for prompt engineering, operation selection, and creative applications

### Changed
- **FastMCP Upgrade**: Upgraded from 2.12.0+ to 2.14.3 with sampling support
- **Tool Architecture**: Now 16 consolidated portmanteau tools (50% reduction from original 28)
- **Documentation**: Enhanced with sampling workflow guides and extended usage examples

### Technical
- **SEP-1577 Compliance**: Full implementation of "sampling with tools" specification
- **Async Orchestration**: Proper timing and sequencing for complex avatar behaviors
- **Context Awareness**: Workflow parameters with environmental and timing context
- **Safety Controls**: Configurable iteration limits (1-20) to prevent infinite loops

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
